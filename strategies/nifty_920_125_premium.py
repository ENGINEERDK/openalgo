# 🔁 OpenAlgo Python Bot is running.

from openalgo import api
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, time
import pytz
import math
import time as t
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =========================
# CONFIG
# =========================
API_KEY = os.getenv("API_KEY")
HOST = os.getenv("HOST", "http://127.0.0.1:5000")
WS_URL = os.getenv("WS_URL", "ws://127.0.0.1:8765")

# Validate required environment variables
if not API_KEY:
    raise RuntimeError("API_KEY not found in environment variables. Please set it in your .env file or PythonAnywhere environment.")

STRATEGY = "Nifty_920_125Premium"

UNDERLYING = "NIFTY"
INDEX_EXCHANGE = "NSE_INDEX"
OPTION_EXCHANGE = "NFO"

TARGET_PREMIUM = 125
SL_PERCENT = 25
MAX_TRADE_LEGS = 6   # 3 CE + 3 PE

CAPITAL = 500000
CAPITAL_PER_SET = 150000
LOT_SIZE = 75

START_TIME = time(9, 20)
STOP_TIME = time(14, 50)
SQUARE_OFF_TIME = time(15, 10)

ist = pytz.timezone("Asia/Kolkata")

# =========================
# STATE
# =========================
client = api(api_key=API_KEY, host=HOST, ws_url=WS_URL, verbose=True)

active_pair = {}
completed_legs = 0
can_trade = True

# =========================
# UTILS
# =========================
def now_ist():
    return datetime.now(ist)

def within_entry_time():
    return START_TIME <= now_ist().time() <= STOP_TIME

def calc_lots():
    lots = math.floor(CAPITAL_PER_SET / (TARGET_PREMIUM * LOT_SIZE))
    return max(1, lots)

def round_strike(price):
    return round(price / 50) * 50

# =========================
# MARKET DATA
# =========================
def get_nifty_ltp():
    q = client.quotes(symbol="NIFTY", exchange=INDEX_EXCHANGE)
    return q["data"]["ltp"]

def fetch_chain(strike):
    return client.optionschain(
        underlying=UNDERLYING,
        exchange=INDEX_EXCHANGE,
        strike_price=strike,
        depth=10
    )

def closest_option(options):
    return min(options, key=lambda x: abs(x["ltp"] - TARGET_PREMIUM))

# =========================
# ORDER FUNCTIONS
# =========================
def sell_option(symbol, qty):
    return client.placeorder(
        strategy=STRATEGY,
        symbol=symbol,
        exchange=OPTION_EXCHANGE,
        action="SELL",
        quantity=qty,
        pricetype="MARKET",
        product="MIS"
    )

def place_sl(symbol, entry):
    sl = round(entry * (1 + SL_PERCENT / 100), 1)
    client.placeorder(
        strategy=STRATEGY,
        symbol=symbol,
        exchange=OPTION_EXCHANGE,
        action="BUY",
        quantity=LOT_SIZE,
        pricetype="SL-M",
        trigger_price=sl,
        product="MIS"
    )

# =========================
# ENTRY LOGIC
# =========================
def enter_trade():
    global active_pair, completed_legs, can_trade

    if not can_trade or not within_entry_time():
        return

    if completed_legs >= MAX_TRADE_LEGS or active_pair:
        return

    nifty = get_nifty_ltp()
    atm = round_strike(nifty)
    chain = fetch_chain(atm)

    ce = closest_option(chain["CE"])
    pe = closest_option(chain["PE"])

    lots = calc_lots()
    qty = lots * LOT_SIZE

    sell_option(ce["symbol"], qty)
    sell_option(pe["symbol"], qty)

    place_sl(ce["symbol"], ce["ltp"])
    place_sl(pe["symbol"], pe["ltp"])

    active_pair = {
        "CE": ce["symbol"],
        "PE": pe["symbol"]
    }

    print(f"✅ Trade Entered | CE: {ce['symbol']} | PE: {pe['symbol']}")

# =========================
# WEBSOCKET CALLBACK
# =========================
def on_ltp(data):
    global active_pair, completed_legs

    if not active_pair:
        return

    symbol = data["symbol"]
    ltp = data["data"]["ltp"]

    if symbol not in active_pair.values():
        return

    pos = client.openposition(strategy=STRATEGY, symbol=symbol, exchange=OPTION_EXCHANGE)

    if int(pos.get("quantity", 0)) == 0:
        completed_legs += 1
        active_pair.pop("CE" if "CE" in symbol else "PE", None)

        # trail remaining leg
        for s in active_pair.values():
            trail = round(ltp * (1 + SL_PERCENT / 100), 1)
            client.placeorder(
                strategy=STRATEGY,
                symbol=s,
                exchange=OPTION_EXCHANGE,
                action="BUY",
                quantity=LOT_SIZE,
                pricetype="SL-M",
                trigger_price=trail,
                product="MIS"
            )

# =========================
# SCHEDULER
# =========================
scheduler = BackgroundScheduler(timezone=ist)
scheduler.add_job(enter_trade, "interval", seconds=10)

def square_off():
    print("⏹ Square off triggered")
    client.closeposition(strategy=STRATEGY)

scheduler.add_job(square_off, "cron", hour=15, minute=10)
scheduler.start()

# =========================
# WEBSOCKET START
# =========================
client.connect()
client.subscribe_ltp(
    instruments=[
        {"exchange": OPTION_EXCHANGE, "symbol": "*"}
    ],
    on_data_received=on_ltp
)

# =========================
# KEEP ALIVE
# =========================
while True:
    t.sleep(1)
