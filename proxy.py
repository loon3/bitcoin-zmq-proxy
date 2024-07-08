import asyncio
import websockets
import zmq
import zmq.asyncio

BITCOIN_ZMQ_ADDRESS = "tcp://0.0.0.0:9333"  # Change this to your Bitcoin ZMQ address
WEBSOCKET_PORT = 8765

async def zmq_listener():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(BITCOIN_ZMQ_ADDRESS)
    socket.setsockopt_string(zmq.SUBSCRIBE, '')

    while True:
        msg = await socket.recv_multipart()
        print(f"Received ZMQ message: {msg}")  # Add this line
        yield msg

async def ws_handler(websocket, path):
    listener_task = asyncio.create_task(zmq_listener())
    ping_task = asyncio.create_task(ping(websocket))

    async for msg in zmq_listener():
        print(f"Sending WebSocket message: {msg}")  # Add this line
        await websocket.send(str(msg))

    await listener_task
    await ping_task

async def ping(websocket):
    while True:
        await asyncio.sleep(60)
        await websocket.send("ping")

async def main():
    async with websockets.serve(ws_handler, "0.0.0.0", WEBSOCKET_PORT):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
