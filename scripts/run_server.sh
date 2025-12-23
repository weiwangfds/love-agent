#!/bin/bash
export PYTHONPATH=.
export DASHSCOPE_API_KEY="${DASHSCOPE_API_KEY}"
python3 src/server.py
