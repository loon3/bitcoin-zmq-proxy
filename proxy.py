import asyncio
import websockets
import zmq
import zmq.asyncio
import json
from bitcoin.core import CBlock
from bitcoin.core.serialize import deserialize
from bitcoin.core import lx

BITCOIN_ZMQ_ADDRESS = "tcp://bitcoind:9333"  # Use the container name as the address
WEBSOCKET_PORT = 8765

async def zmq_listener():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(BITCOIN_ZMQ_ADDRESS)
    socket.setsockopt_string(zmq.SUBSCRIBE, 'rawblock')

    while True:
        msg = await socket.recv_multipart()
        print(f"Received ZMQ message: {msg}")
        yield msg

def get_block_info(raw_block):
    block = CBlock.deserialize(raw_block)
    block_info = {
        'height': block.nHeight,
        'time': block.nTime
    }
    return block_info

async def zmq_listener_task(websocket):
    async for msg in zmq_listener():
        raw_block = msg[1]
        block_info = get_block_info(raw_block)
        block_info_json = json.dumps(block_info)
        print(f"Sending WebSocket message: {block_info_json}")
        await websocket.send(block_info_json)

async def ws_handler(websocket, path):
    listener_task = asyncio.create_task(zmq_listener_task(websocket))
    ping_task = asyncio.create_task(ping(websocket))
    
    done, pending = await asyncio.wait(
        [listener_task, ping_task],
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
