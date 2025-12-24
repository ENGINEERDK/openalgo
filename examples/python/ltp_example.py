"""
OpenAlgo WebSocket Feed Example
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
    {"exchange": "NSE", "symbol": "TCS",
     "exchange": "NSE", "symbol": "INFY"
     }
]

def on_data_received(data):
    print("LTP Update:")
    print(data)

# Connect and subscribe
client.connect()
client.subscribe_ltp(instruments_list, on_data_received=on_data_received)

# Poll LTP data a few times
for i in range(100):
    print(f"\nPoll {i+1}:")
    print(client.get_ltp())
    time.sleep(0.5)

# Cleanup
client.unsubscribe_ltp(instruments_list)
client.disconnect()