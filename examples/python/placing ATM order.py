from openalgo import api

print("🔁 OpenAlgo Python Bot is running.")

# ------------------------------------------
# Initialize API client
# ------------------------------------------
client = api(
    api_key="41621d20a62b07eb1e36f6607dedebe95e3fd2c3086a1197bb1ce956d2539899",
    host="http://ec2-13-201-194-113.ap-south-1.compute.amazonaws.com:5000"
)

# ------------------------------------------
# Fetch NIFTY Spot (must print immediately)
# ------------------------------------------
quote = client.quotes(symbol="NIFTY", exchange="NSE_INDEX")
print("NIFTY QUOTE:", quote)

# ------------------------------------------
# Place NIFTY ATM Option Order - 09DEC25
# ------------------------------------------
response = client.optionsorder(
      strategy="python",
      underlying="NIFTY",          # Underlying Index
      exchange="NSE_INDEX",        # Index exchange
      expiry_date="23DEC25",       # Correct expiry
      offset="OTM2",                # Auto-select ATM strike
      option_type="CE",            # CE or PE
      action="BUY",                # BUY or SELL
      quantity=75,                 # 1 Lot = 75
      pricetype="MARKET",          # MARKET or LIMIT
      product="NRML",              # NRML or MIS
      splitsize=0                  # 0 = no split
)

print("ORDER RESPONSE:", response)
