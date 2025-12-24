"""
OpenAlgo WebSocket Quote Feed Example
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
    {"exchange": "NSE_INDEX", "symbol": "NIFTY"},
    {"exchange": "NSE", "symbol": "INFY"},
    {"exchange": "NSE", "symbol": "TCS"}
]

def on_data_received(data):
    print("Quote Update:")
    print(data)

# Connect and subscribe
client.connect()
client.subscribe_quote(instruments_list, on_data_received=on_data_received)

# Poll Quote data a few times
for i in range(100):
    print(f"\nPoll {i+1}:")
    print(client.get_quotes())
    time.sleep(0.5)

# Cleanup
client.unsubscribe_quote(instruments_list)
client.disconnect()