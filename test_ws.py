import asyncio
import websockets

async def test():
    uri = "wss://ciftlik.rifatseker.com.tr/ws/live"
    try:
        async with websockets.connect(uri) as websocket:
            print("Successfully connected to websocket!")
            data = await websocket.recv()
            print("Received data:", data[:100], "...")
    except Exception as e:
        print("Failed to connect:", e)

asyncio.run(test())
