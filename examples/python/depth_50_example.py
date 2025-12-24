"""
OpenAlgo WebSocket 50-Level Market Depth Example
For brokers that support deep market depth (Fyers TBT, etc.)
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

# Instruments for 50-level depth testing
# Use :50 suffix to request 50-level TBT depth (e.g., "TCS:50")
instruments_list = [
    {"exchange": "NSE", "symbol": "TCS:50"}
]

def on_data_received(data):
    print("Market Depth Update:")
    print(data)

# Connect and subscribe
client.connect()
client.subscribe_depth(instruments_list, on_data_received=on_data_received)

# Wait a bit for WebSocket to connect and start receiving data
print("\nWaiting for TBT WebSocket to connect and receive data...")
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
