#!/bin/sh
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
export PYTHONPATH="$DIR:$DIR/src:$PYTHONPATH"

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
    test)
        coverage run --branch --source=src -m unittest discover -s tests -v
        coverage report -m
        ;;
    *)
        python3 src/rpc_server.py &
        SERVER_PID=$!
        sleep 1
        python3 src/demo_client.py
        kill "$SERVER_PID" 2>/dev/null || true
        ;;
esac