from openalgo import api
from config import API_KEY, HOST
from datetime import datetime

print("🔁 OpenAlgo Python Bot is running.")

# ------------------------------------------
# Initialize API client
# ------------------------------------------
client = api(
    api_key=API_KEY,
    host=HOST
)

# ------------------------------------------
# Fetch NIFTY Spot (must print immediately)
# ------------------------------------------
quote = client.quotes(symbol="NIFTY", exchange="NSE_INDEX")
print("NIFTY QUOTE:", quote)

# ------------------------------------------
# Get Next Closest Expiry Date Programmatically
# ------------------------------------------
def get_next_expiry():
    """Fetch the next closest expiry date for NIFTY options"""
    try:
        expiry_response = client.expiry(
            symbol="NIFTY",
            exchange="NFO",
            instrumenttype="options",
            expirytype="weekly"
        )
        
        if expiry_response['status'] == 'success' and expiry_response['data']:
            # Get current week expiry (next closest)
            next_expiry = expiry_response['data']['current_week']
            print(f"Next closest expiry selected: {next_expiry}")
            return next_expiry
        else:
            print("Failed to fetch expiry dates, using fallback date")
            return "26DEC25"  # Fallback date
    except Exception as e:
        print(f"Error fetching expiry: {e}, using fallback date")
        return "26DEC25"  # Fallback date

# Get the next available expiry
expiry_date = get_next_expiry()

# ------------------------------------------
# Place NIFTY ATM Option Order - Dynamic Expiry
# ------------------------------------------
response = client.optionsorder(
      strategy="python",
      underlying="NIFTY",          # Underlying Index
      exchange="NSE_INDEX",        # Index exchange
      expiry_date=expiry_date,     # Dynamically selected expiry
      offset="OTM2",                # Auto-select ATM strike
      option_type="CE",            # CE or PE
      action="BUY",                # BUY or SELL
      quantity=75,                 # 1 Lot = 75
      pricetype="MARKET",          # MARKET or LIMIT
      product="NRML",              # NRML or MIS
      splitsize=0                  # 0 = no split
)

print("ORDER RESPONSE:", response)
