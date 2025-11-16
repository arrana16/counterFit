from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import Body, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.connection_manager import ConnectionManager
from models.session import Session
from schemas.session import SessionCreateRequest

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
def ping():
    return {"msg": "pong"}


manager = ConnectionManager()


SESSIONS: Dict[str, Session] = {}


class SelectItemRequest(BaseModel):
    item_id: str


@app.post("/api/session", response_model=Session)
def create_session(
    session_data: Optional[SessionCreateRequest] = Body(default=None),
) -> Session:
    session_payload = session_data.dict(exclude_unset=True) if session_data else {}
    session_id = str(uuid4())
    session = Session(session_id=session_id, **session_payload)
    SESSIONS[session_id] = session
    return session


@app.get("/api/sessions", response_model=List[Session])
def list_sessions() -> List[Session]:
    return list(SESSIONS.values())


@app.post("/api/session/{session_id}/select_item")
def select_item(session_id: str, payload: SelectItemRequest) -> Dict[str, str]:
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    session.selected_item_id = payload.item_id
    return {"session_id": session_id, "selected_item_id": payload.item_id}


@app.websocket("/ws/session/{session_id}")
async def ws_session(ws: WebSocket, session_id: str):
    connection = await manager.connect(session_id, ws)
    await manager.send_personal_message(
        ws,
        {
            "type": "status",
            "payload": f"connected as {connection.client_id} in session {session_id}",
        },
    )
    await manager.broadcast(
        session_id,
        {
            "type": "status",
            "payload": f"{connection.client_id} joined",
        },
    )

    try:
        while True:
            payload = await ws.receive_text()
            await manager.broadcast(
                session_id,
                {
                    "type": "message",
                    "from": connection.client_id,
                    "payload": payload,
                },
            )
    except WebSocketDisconnect:
        manager.disconnect(session_id, ws)
        await manager.broadcast(
            session_id,
            {
                "type": "status",
                "payload": f"{connection.client_id} left",
            },
        )
