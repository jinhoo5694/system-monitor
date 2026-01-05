#!/bin/bash
# Launch script for System Monitor

cd "$(dirname "$0")"
source venv/bin/activate
python3 system_monitor.py
