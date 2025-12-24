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
        # Fetch expiry dates using the correct SDK method
        print("Fetching NIFTY expiry dates...")
        expiry_response = client.expiry(
            symbol="NIFTY",
            exchange="NFO",
            instrumenttype="options"
        )
        
        print(f"Expiry API Response: {expiry_response}")
        
        if expiry_response.get('status') == 'success' and expiry_response.get('data'):
            expiry_dates = expiry_response['data']
            
            if isinstance(expiry_dates, list) and len(expiry_dates) > 0:
                # Get the first (nearest) expiry date
                next_expiry = expiry_dates[0]
                print(f"Using nearest expiry: {next_expiry}")
                
                # Convert from DD-MMM-YY format to DDMMMYY format for options order
                from datetime import datetime
                try:
                    # Parse the date format DD-MMM-YY (e.g., "26-DEC-25")
                    expiry_date = datetime.strptime(next_expiry, "%d-%b-%y")
                    # Format to DDMMMYY (e.g., "26DEC25")
                    formatted_expiry = expiry_date.strftime("%d%b%y").upper()
                    print(f"Formatted expiry for order: {formatted_expiry}")
                    return formatted_expiry
                except Exception as format_error:
                    print(f"Date formatting error: {format_error}, using original format: {next_expiry}")
                    return next_expiry
            else:
                print(f"No expiry dates found in response data: {expiry_dates}")
        else:
            print(f"API Error: {expiry_response.get('message', 'Unknown error')}")
        
        print("Using fallback expiry date")
        return "26DEC25"  # Fallback date
        
    except Exception as e:
        print(f"Error fetching expiry: {e}")
        print("Using fallback expiry date")
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
