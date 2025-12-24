from openalgo import api
from config import API_KEY, HOST

# Initialize client with parameters from config
client = api(api_key=API_KEY, host=HOST)

# Fetch multiple quotes
response = client.multiquotes(symbols=[
    {"symbol": "RELIANCE", "exchange": "NSE"},
    {"symbol": "TCS", "exchange": "NSE"},
    {"symbol": "INFY", "exchange": "NSE"}
])

print(response)

