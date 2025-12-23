#!/bin/bash
export PYTHONPATH=.
if [ -f .env ]; then
    export $(cat .env | xargs)
fi
export DASHSCOPE_API_KEY="${DASHSCOPE_API_KEY}"
python3 src/server.py
