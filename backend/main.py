from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import Body, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from services.connection_manager import ConnectionManager
from agents import LISTINGS, analyst_agent

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


class Session(BaseModel):
    session_id: str
    mode: str = "auto"
    selected_item_id: Optional[str] = None
    buyer_agent: Optional[Dict[str, Any]] = None
    evaluator_agents: List[Dict[str, Any]] = Field(default_factory=list)
    seller_agents: List[Dict[str, Any]] = Field(default_factory=list)
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    turn: int = 0


class SessionCreateRequest(BaseModel):
    mode: Optional[str] = "auto"
    selected_item_id: Optional[str] = None
    buyer_agent: Optional[Dict[str, Any]] = None
    evaluator_agents: Optional[List[Dict[str, Any]]] = None
    seller_agents: Optional[List[Dict[str, Any]]] = None
    messages: Optional[List[Dict[str, Any]]] = None
    turn: Optional[int] = 0


class SelectItemRequest(BaseModel):
    item_id: str


SESSIONS: Dict[str, Session] = {}


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

    session = SESSIONS.get(session_id)
    if session is None:
        await ws.send_json({"type": "error", "detail": "Session not found"})
        await ws.close(code=1008)
        return

    listing_id = session.selected_item_id
    listing = LISTINGS.get(listing_id) if listing_id else None

    print("DEBUG LISTINGS KEYS:", LISTINGS.keys())
    print("DEBUG SELECTED ITEM:", listing_id)
    print("DEBUG LOOKUP RESULT:", listing)

    if listing is None:
        detail = (
            "No listing selected for this session"
            if not listing_id
            else "Selected listing not found"
        )
        await ws.send_json({"type": "error", "detail": detail})
    else:
        analyst_output = await analyst_agent(listing)
        await ws.send_json(
            {
                "type": "agent_output",
                "agent": "Analyst",
                "content": analyst_output,
            }
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
