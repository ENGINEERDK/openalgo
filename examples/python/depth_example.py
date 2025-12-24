"""
OpenAlgo WebSocket Market Depth Example
"""

from openalgo import api
import time
from config import API_KEY, HOST, WS_URL

# Initialize feed client with parameters from config
client = api(
    api_key=API_KEY,
    host=HOST,
    ws_url=WS_URL
)

# MCX instruments for testing
instruments_list = [

    {"exchange": "NSE", "symbol": "TCS"}
]

def on_data_received(data):
    print("Market Depth Update:")
    print(data)

# Connect and subscribe
client.connect()
client.subscribe_depth(instruments_list, on_data_received=on_data_received)

# Poll Market Depth data a few times
for i in range(100):
    print(f"\nPoll {i+1}:")
    print(client.get_depth())
    time.sleep(0.5)

# Cleanup
client.unsubscribe_depth(instruments_list)
client.disconnect()