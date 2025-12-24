"""
OpenAlgo WebSocket 20-Level Market Depth Example
For brokers that support 20-level depth (Dhan NSE/NFO)
"""

from openalgo import api
import time
import logging
from config import API_KEY, HOST, WS_URL

# Configure logging to see WebSocket debug output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize feed client with parameters from config
client = api(
    api_key=API_KEY,
    host=HOST,
    ws_url=WS_URL
)

# Instruments for 20-level depth testing
# Use :20 suffix to request 20-level depth (e.g., "TCS:20")
# NFO also supports 20-level depth
instruments_list = [
    {"exchange": "NSE", "symbol": "TCS:20"},
]

def on_data_received(data):
    print("Market Depth Update:")
    print(data)

# Connect and subscribe
client.connect()
client.subscribe_depth(instruments_list, on_data_received=on_data_received)

# Wait a bit for WebSocket to connect and start receiving data
print("\nWaiting for 20-level depth WebSocket to connect and receive data...")
time.sleep(3)

# Poll Market Depth data a few times
for i in range(15):
    print(f"\nPoll {i+1}:")
    depth = client.get_depth()
    if depth:
        print(depth)
    else:
        print("No depth data yet...")
    time.sleep(1)

# Cleanup
client.unsubscribe_depth(instruments_list)
client.disconnect()
