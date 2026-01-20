#!/bin/bash
# Python execution tool

SCRIPT=$1

if [ -z "$SCRIPT" ]; then
    echo "Usage: python_exec.sh <script.py>"
    exit 1
fi

python3 "$SCRIPT"
