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
        print(f"Received ZMQ message: {msg}")
        yield msg

async def zmq_check():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(BITCOIN_ZMQ_ADDRESS)
    socket.setsockopt_string(zmq.SUBSCRIBE, '')

    while True:
        try:
            await socket.recv_multipart(flags=zmq.NOBLOCK)
            print("ZMQ address is being listened to.")
            yield True
        except zmq.Again:
            print("No message received from ZMQ address.")
            yield False
        await asyncio.sleep(60)

async def ws_handler(websocket, path):
    zmq_listener_task = asyncio.create_task(zmq_listener())
    zmq_check_task = asyncio.create_task(zmq_check())

    while True:
        listener_msg = await zmq_listener_task
        check_msg = await zmq_check_task

        if listener_msg:
            print(f"Sending WebSocket message: {listener_msg}")
            await websocket.send(str(listener_msg))

        if check_msg:
            print(f"Sending WebSocket check result: {check_msg}")
            await websocket.send(str(check_msg))

async def main():
    async with websockets.serve(ws_handler, "0.0.0.0", WEBSOCKET_PORT):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
