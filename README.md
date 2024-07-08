## Overview

This project sets up a WebSocket server that listens to ZMQ messages from Bitcoin and Counterparty nodes and forwards them to WebSocket clients.

## Files

- `proxy.py`: The main script that sets up the WebSocket server and handles ZMQ messages.
- `requirements.txt`: Lists the Python dependencies required for the project.
- `Dockerfile`: Defines the Docker image for the project.

## Setup

These steps assume you have a running counterparty-core and bitcoind node using docker on the same machine.

1. **Clone the repository:**

    ```sh
    git clone https://github.com/loon3/bitcoin-zmq-proxy.git
    cd bitcoin-zmq-proxy
    ```

2. **Build the Docker image:**

    ```sh
    docker build -t bitcoin-zmq-proxy .
    ```

3. **Create a new network:**

    ```sh
    docker network create zmq-websocket-proxy
    ```

4. **Add counterparty-core and bitcoind containers to the network:**

    (Note: may need to run docker ps to get the container names)

    ```sh
    docker network connect zmq-websocket-proxy counterparty-core-counterparty-core-1 
    docker network connect zmq-websocket-proxy counterparty-core-bitcoind-1
    ```

5. **Run the Docker container:**

    ```sh
    docker run -p 8765:8765 -d --network zmq-websocket-proxy bitcoin-zmq-proxy
    ```

    This will start the WebSocket server on port 8765.

## Usage

1. **Connect to the WebSocket server:**

    Use a WebSocket client to connect to `ws://<server-ip>:8765`.

2. **Receive messages:**

    The server will forward ZMQ messages from the Bitcoin and Counterparty nodes to the connected WebSocket clients.

## Configuration

- **BITCOIN_ZMQ_ADDRESS**: The ZMQ address of the Bitcoin node. Default is `tcp://counterparty-core-bitcoind-1:9333`.
- **COUNTERPARTY_ZMQ_ADDRESS**: The ZMQ address of the Counterparty node. Default is `tcp://counterparty-core-counterparty-core-1:4001`.
- **WEBSOCKET_PORT**: The port on which the WebSocket server will run. Default is `8765`.

You can change these configurations in the `proxy.py` file.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
