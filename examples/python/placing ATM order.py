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
        # Try weekly expiries first
        print("Fetching NIFTY weekly expiry dates...")
        expiry_response = client.expiry(
            symbol="NIFTY",
            exchange="NFO",
            instrumenttype="options",
            expirytype="weekly"
        )
        
        print(f"Expiry API Response: {expiry_response}")
        
        if expiry_response.get('status') == 'success' and expiry_response.get('data'):
            data = expiry_response['data']
            
            # Try different possible keys for current/next expiry
            if 'current_week' in data and data['current_week']:
                next_expiry = data['current_week']
                print(f"Using current_week expiry: {next_expiry}")
                return next_expiry
            elif 'next_week' in data and data['next_week']:
                next_expiry = data['next_week']
                print(f"Using next_week expiry: {next_expiry}")
                return next_expiry
            elif isinstance(data, list) and len(data) > 0:
                next_expiry = data[0]
                print(f"Using first available expiry: {next_expiry}")
                return next_expiry
            else:
                print(f"Unexpected data structure: {data}")
        
        # If weekly fails, try monthly
        print("Weekly expiry failed, trying monthly expiry...")
        expiry_response = client.expiry(
            symbol="NIFTY",
            exchange="NFO",
            instrumenttype="options",
            expirytype="monthly"
        )
        
        print(f"Monthly Expiry API Response: {expiry_response}")
        
        if expiry_response.get('status') == 'success' and expiry_response.get('data'):
            data = expiry_response['data']
            if 'current_month' in data and data['current_month']:
                next_expiry = data['current_month']
                print(f"Using current_month expiry: {next_expiry}")
                return next_expiry
            elif isinstance(data, list) and len(data) > 0:
                next_expiry = data[0]
                print(f"Using first monthly expiry: {next_expiry}")
                return next_expiry
        
        print("All expiry methods failed, using fallback date")
        return "26DEC25"  # Fallback date
        
    except Exception as e:
        print(f"Error fetching expiry: {e}")
        print("Using fallback date")
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
