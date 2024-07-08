import asyncio
import websockets
import zmq
import zmq.asyncio
import binascii
import json

BITCOIN_ZMQ_ADDRESS = "tcp://counterparty-core-bitcoind-1:9333"  # Change this to your Bitcoin ZMQ address
COUNTERPARTY_ZMQ_ADDRESS = "tcp://counterparty-core-counterparty-core-1:4001"  # Change this to your Counterparty ZMQ address
WEBSOCKET_PORT = 8775

async def zmq_listener(socket):
    while True:
        msg = await socket.recv_multipart()
        yield msg

async def zmq_listener_task(websocket, filters):
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.RCVHWM, 0)
    socket.connect(BITCOIN_ZMQ_ADDRESS)
    socket.setsockopt_string(zmq.SUBSCRIBE, 'rawblock')
    socket.connect(COUNTERPARTY_ZMQ_ADDRESS)
    socket.setsockopt_string(zmq.SUBSCRIBE, '')

    async for msg in zmq_listener(socket):
        try:
            # Assuming the second element is the JSON string
            json_str = msg[1].decode('utf-8')
            json_obj = json.loads(json_str)

            # Filter the message based on the filters received from the WebSocket client
            if "event" in json_obj and json_obj["event"] in filters:
                await websocket.send(json.dumps(json_obj))
        except (IndexError, UnicodeDecodeError, json.JSONDecodeError) as e:
            print(f"Error processing message: {e}")
            await websocket.send(str(msg))

async def ws_handler(websocket, path):
    try:
        # Receive the initial message containing the filters
        initial_message = await websocket.recv()
        message_data = json.loads(initial_message)
        filters = message_data.get("filters", [])
        print(f"Received filters: {filters}")

        listener_task = asyncio.create_task(zmq_listener_task(websocket, filters))
        
        done, pending = await asyncio.wait(
            [listener_task], 
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")

async def main():
    async with websockets.serve(ws_handler, "0.0.0.0", WEBSOCKET_PORT):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
