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
    async for msg in zmq_listener():
        print(f"Sending WebSocket message: {msg}")  # Add this line
        await websocket.send(str(msg))

async def main():
    async with websockets.serve(ws_handler, "0.0.0.0", WEBSOCKET_PORT):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
