#!/bin/sh
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

case "$1" in
    server)
        python3 src/rpc_server.py
        ;;
    client)
        python3 src/demo_client.py
        ;;
    repl)
        python3 src/repl.py
        ;;
    *)
        python3 src/rpc_server.py &
        SERVER_PID=$!
        sleep 1
        python3 src/demo_client.py
        kill "$SERVER_PID" 2>/dev/null || true
        ;;
esac