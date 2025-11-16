from typing import Dict, List

from fastapi import WebSocket


class Connection:
    """Lightweight wrapper that keeps track of a websocket and its id."""

    def __init__(self, websocket: WebSocket, client_id: str):
        self.websocket = websocket
        self.client_id = client_id


class ConnectionManager:
    """Keeps track of websocket connections grouped by session."""

    def __init__(self) -> None:
        self.sessions: Dict[str, List[Connection]] = {}
        self._client_counter = 0

    async def connect(self, session_id: str, websocket: WebSocket) -> Connection:
        await websocket.accept()
        self._client_counter += 1
        connection = Connection(websocket, client_id=f"client-{self._client_counter}")
        self.sessions.setdefault(session_id, []).append(connection)
        return connection

    def disconnect(self, session_id: str, websocket: WebSocket) -> None:
        connections = self.sessions.get(session_id, [])
        self.sessions[session_id] = [
            conn for conn in connections if conn.websocket is not websocket
        ]
        if not self.sessions[session_id]:
            self.sessions.pop(session_id, None)

    async def broadcast(self, session_id: str, message: dict) -> None:
        for connection in self.sessions.get(session_id, []):
            await connection.websocket.send_json(message)

    async def send_personal_message(self, websocket: WebSocket, message: dict) -> None:
        await websocket.send_json(message)
