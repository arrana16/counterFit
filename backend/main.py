from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

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

@app.websocket("/ws/session/{session_id}")
async def ws_session(ws: WebSocket, session_id: str):
    await ws.accept()
    await ws.send_json({"type": "status", "payload": "connected"})
