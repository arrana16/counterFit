from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from services.connection_manager import ConnectionManager

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
