import asyncio
import json
import os
from typing import Optional

import websockets


async def reader(ws: websockets.WebSocketClientProtocol) -> None:
    try:
        async for message in ws:
            try:
                parsed = json.loads(message)
            except json.JSONDecodeError:
                print(f"< raw: {message}")
            else:
                print(f"< {json.dumps(parsed, indent=2)}")
    except websockets.ConnectionClosedOK:
        print("Connection closed by server")


async def writer(
    ws: websockets.WebSocketClientProtocol, initial_message: Optional[str]
) -> None:
    loop = asyncio.get_running_loop()
    if initial_message:
        await ws.send(initial_message)

    print("Type a message and press enter to send it. Leave blank to quit.")
    while True:
        message = await loop.run_in_executor(None, input, "> ")
        if not message.strip():
            await ws.close()
            break
        await ws.send(message)


async def main() -> None:
    session_id = os.environ.get("SESSION_ID", "demo")
    uri = os.environ.get(
        "WS_URI", f"ws://localhost:8000/ws/session/{session_id}"
    )
    initial_message = os.environ.get("WS_MESSAGE")
    print(f"Connecting to {uri}")

    async with websockets.connect(uri) as websocket:
        await asyncio.gather(
            reader(websocket),
            writer(websocket, initial_message),
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
