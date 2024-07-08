import asyncio
import websockets
import zmq
import zmq.asyncio
import binascii

BITCOIN_ZMQ_ADDRESS = "tcp://counterparty-core-bitcoind-1:9333"  # Change this to your Bitcoin ZMQ address
COUNTERPARTY_ZMQ_ADDRESS = "tcp://counterparty-core-counterparty-core-1:4001"  # Change this to your Counterparty ZMQ address
WEBSOCKET_PORT = 8765

async def zmq_listener(socket):
    while True:
        msg = await socket.recv_multipart()
        print(f"Received ZMQ message: {msg}")
        yield msg

async def zmq_listener_task(websocket):
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.RCVHWM, 0)
    socket.connect(BITCOIN_ZMQ_ADDRESS)
    socket.setsockopt_string(zmq.SUBSCRIBE, 'rawblock')
    socket.connect(COUNTERPARTY_ZMQ_ADDRESS)
    socket.setsockopt_string(zmq.SUBSCRIBE, '')

    async for msg in zmq_listener(socket):
        print(f"Sending WebSocket message: {msg}")
        # txid_bytes = msg[1]
        # txid_hex = binascii.hexlify(txid_bytes).decode('utf-8')
        # await websocket.send(txid_hex)
        await websocket.send(str(msg))

async def ws_handler(websocket, path):
    listener_task = asyncio.create_task(zmq_listener_task(websocket))
    # ping_task = asyncio.create_task(ping(websocket))
    
    done, pending = await asyncio.wait(
        [listener_task], # add ping_task here for testing
        return_when=asyncio.FIRST_COMPLETED,
    )
    
    for task in pending:
        task.cancel()

async def ping(websocket):
    while True:
        await asyncio.sleep(60)
        print("Sending ping")
        await websocket.send("ping")

async def main():
    async with websockets.serve(ws_handler, "0.0.0.0", WEBSOCKET_PORT):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())