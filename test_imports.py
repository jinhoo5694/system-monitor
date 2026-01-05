#!/usr/bin/env python3
"""Test script to verify imports and basic functionality"""

import sys
import psutil
from collections import deque

print("Testing imports and basic functionality...")

# Test psutil
print(f"✓ psutil version: {psutil.__version__}")
print(f"  CPU: {psutil.cpu_percent(interval=0.5)}%")
print(f"  Memory: {psutil.virtual_memory().percent}%")

# Test deque
test_deque = deque([1, 2, 3], maxlen=5)
test_deque.append(4)
print(f"✓ deque working: {list(test_deque)}")

# Test data collection
cpu_history = deque([0] * 60, maxlen=60)
for i in range(5):
    cpu_history.append(i * 10)
print(f"✓ Data history working: last 5 values = {list(cpu_history)[-5:]}")

print("\n✓ All basic tests passed!")
print("\nNote: tkinter GUI test requires display and cannot be run in headless mode.")
print("To fully test the application, run: ./run.sh")
