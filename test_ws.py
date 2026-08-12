import asyncio
import websockets

async def test():
    uri = "ws://127.0.0.1:8000/ws/test"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            await websocket.send("Hello")
            response = await websocket.recv()
            print(f"Received: {response}")
    except Exception as e:
        print(f"Failed to connect: {e}")

asyncio.run(test())
