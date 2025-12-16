# 🔁 OpenAlgo Python Bot is running.

import logging
from openalgo import api
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, time
import pytz
import math
import time as t
import os
from dotenv import load_dotenv

# =========================
# LOGGING
# =========================
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# =========================
# ENV
# =========================
load_dotenv()

API_KEY = "e493641929e1d2e9b37b9b850069e8cd06788db937bce4c0155e4564cbf8b5f7"
HOST = os.getenv("HOST_SERVER", "http://127.0.0.1:5000")
WS_URL = os.getenv("WS_URL", "ws://127.0.0.1:8765")

STRATEGY = "Nifty_920_125Premium"

UNDERLYING = "NIFTY"
INDEX_EXCHANGE = "NSE_INDEX"
OPTION_EXCHANGE = "NFO"

TARGET_PREMIUM = 125
SL_PERCENT = 25
MAX_TRADE_LEGS = 6

CAPITAL = 500000
CAPITAL_PER_SET = 150000
LOT_SIZE = 75

START_TIME = time(9, 20)
STOP_TIME = time(14, 50)
SQUARE_OFF_TIME = time(15, 10)

ist = pytz.timezone("Asia/Kolkata")

# =========================
# CLIENT
# =========================
logger.info("Initializing OpenAlgo client")
client = api(
    api_key=API_KEY,
    host=HOST,
    ws_url=WS_URL,
    verbose=True
)

# =========================
# STATE
# =========================
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
# MARKET DATA (SAFE)
# =========================
def get_nifty_ltp():
    try:
        q = client.quote(symbol="NIFTY", exchange=INDEX_EXCHANGE)
        logger.debug(f"NIFTY quote raw: {q}")

        if not isinstance(q, dict) or q.get("status") != "success":
            logger.error(f"Quote failed: {q}")
            return None

        return q["data"]["ltp"]

    except Exception:
        logger.exception("Error fetching NIFTY LTP")
        return None

def fetch_chain(strike):
    try:
        chain = client.optionchain(
            underlying=UNDERLYING,
            exchange=INDEX_EXCHANGE,
            strike_price=strike,
            depth=10
        )
        logger.debug(f"Option chain raw: {chain}")

        if chain.get("status") != "success":
            logger.error(f"Option chain error: {chain}")
            return None

        return chain["data"]

    except Exception:
        logger.exception("Error fetching option chain")
        return None

def closest_option(options):
    return min(options, key=lambda x: abs(x["ltp"] - TARGET_PREMIUM))

# =========================
# ORDERS
# =========================
def sell_option(symbol, qty):
    logger.info(f"Selling {symbol} qty {qty}")
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
    logger.info(f"Placing SL for {symbol} @ {sl}")
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
# ENTRY LOGIC (SAFE)
# =========================
def enter_trade():
    global active_pair, completed_legs

    try:
        if not can_trade or not within_entry_time():
            return

        if completed_legs >= MAX_TRADE_LEGS or active_pair:
            return

        nifty = get_nifty_ltp()
        if nifty is None:
            logger.warning("Skipping trade cycle: NIFTY LTP unavailable")
            return

        atm = round_strike(nifty)
        chain = fetch_chain(atm)
        if not chain:
            return

        ce = closest_option(chain["CE"])
        pe = closest_option(chain["PE"])

        lots = calc_lots()
        qty = lots * LOT_SIZE

        sell_option(ce["symbol"], qty)
        sell_option(pe["symbol"], qty)

        place_sl(ce["symbol"], ce["ltp"])
        place_sl(pe["symbol"], pe["ltp"])

        active_pair = {"CE": ce["symbol"], "PE": pe["symbol"]}

        logger.info(f"✅ Trade entered CE={ce['symbol']} PE={pe['symbol']}")

    except Exception:
        logger.exception("Unhandled exception in enter_trade")

# =========================
# WS CALLBACK (DEFENSIVE)
# =========================
def on_ltp(data):
    global active_pair, completed_legs

    try:
        if not active_pair:
            return

        symbol = data.get("symbol")
        ltp = data.get("data", {}).get("ltp")

        if not symbol or not ltp:
            return

        if symbol not in active_pair.values():
            return

        pos = client.openposition(
            strategy=STRATEGY,
            symbol=symbol,
            exchange=OPTION_EXCHANGE
        )

        if int(pos.get("quantity", 0)) == 0:
            completed_legs += 1
            active_pair.pop("CE" if "CE" in symbol else "PE", None)
            logger.info(f"Leg exited: {symbol}")

    except Exception:
        logger.exception("Error in WS LTP handler")

# =========================
# SCHEDULER
# =========================
scheduler = BackgroundScheduler(timezone=ist)
scheduler.add_job(enter_trade, "interval", seconds=10)

def square_off():
    logger.info("⏹ Square off triggered")
    client.closeposition(strategy=STRATEGY)

scheduler.add_job(square_off, "cron", hour=15, minute=10)
scheduler.start()

# =========================
# WS START (OPTIONAL)
# =========================
try:
    client.connect()
    client.subscribe_ltp(
        instruments=[{"exchange": OPTION_EXCHANGE, "symbol": "*"}],
        on_data_received=on_ltp
    )
except Exception:
    logger.exception("WebSocket failed, continuing REST-only mode")

# =========================
# KEEP ALIVE
# =========================
while True:
    t.sleep(1)
