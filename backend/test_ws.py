import asyncio
import json
import requests
import websockets

BACKEND = "http://localhost:8000"

ITEM_ID = "demo-item-1"   # Must match one in LISTINGS dict
SESSION_URL = f"{BACKEND}/api/session"
SELECT_URL = f"{BACKEND}/api/session/{{session_id}}/select_item"
WS_URL = "ws://localhost:8000/ws/session/{session_id}"


def create_session():
    print("📌 Creating session...")
    res = requests.post(SESSION_URL)
    res.raise_for_status()
    session_id = res.json()["session_id"]
    print("✔ Session created:", session_id)
    return session_id


def select_item(session_id):
    print("📌 Selecting item...")
    url = SELECT_URL.format(session_id=session_id)
    res = requests.post(url, json={"item_id": ITEM_ID})
    res.raise_for_status()
    print("✔ Item selected:", res.json())


async def listen_ws(session_id):
    print("📌 Connecting to WebSocket...")
    url = WS_URL.format(session_id=session_id)

    async with websockets.connect(url) as ws:
        print("✔ Connected. Listening for messages...\n")
        try:
            while True:
                msg = await ws.recv()
                try:
                    data = json.loads(msg)
                except:
                    data = msg
                print("📥 WS MESSAGE:", json.dumps(data, indent=2), "\n")
        except websockets.exceptions.ConnectionClosed as e:
            print("❌ WS Closed:", e)


async def main():
    session_id = create_session()
    select_item(session_id)
    await listen_ws(session_id)


if __name__ == "__main__":
    asyncio.run(main())
