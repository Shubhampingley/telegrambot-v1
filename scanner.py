import os
import requests
from datetime import datetime
from telegram import Bot

# Load environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ANGEL_API_KEY = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")

# Angel One endpoints
ANGEL_BASE_URL = "https://apiconnect.angelbroking.com/rest/secure/angelbroking"
LOGIN_URL = f"{ANGEL_BASE_URL}/user/v1/loginByPassword"
QUOTES_URL = f"{ANGEL_BASE_URL}/market/v1/quote"

# Session token (you may cache this with Redis or GitHub Secrets)
session_token = ""

# Sample list — replace with all NSE symbols or load from file
symbols = ["RELIANCE-EQ", "TCS-EQ", "INFY-EQ", "HDFCBANK-EQ", "ICICIBANK-EQ", 
           "SBIN-EQ", "HINDUNILVR-EQ", "ITC-EQ", "LT-EQ", "AXISBANK-EQ"]

headers = {
    "X-PrivateKey": ANGEL_API_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json"
}


def fetch_quote(symbol):
    payload = {
        "mode": "FULL",
        "exchange": "NSE",
        "symboltoken": "",
        "tradingsymbol": symbol,
    }

    try:
        r = requests.post(QUOTES_URL, headers=headers, json=payload)
        data = r.json()
        return data["data"]
    except Exception as e:
        print(f"Failed for {symbol}: {e}")
        return None


def send_telegram_message(message):
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="Markdown")


def scan():
    results = []

    for symbol in symbols:
        quote = fetch_quote(symbol)
        if not quote:
            continue

        try:
            ltp = float(quote["lastPrice"])
            day_high = float(quote["high"])
            day_low = float(quote["low"])
            week_52_high = float(quote["week52High"])
            volume = int(quote["volume"])
            avg_volume = int(quote.get("avgVolTradedPerDay", 1))

            if week_52_high and ltp >= 0.97 * week_52_high:
                results.append((symbol, ltp, "52WH"))

            elif ltp == day_high:
                results.append((symbol, ltp, "Day High"))

            elif ltp == day_low:
                results.append((symbol, ltp, "Day Low"))

            elif avg_volume and volume >= 2 * avg_volume:
                results.append((symbol, ltp, "High Vol"))

        except Exception as e:
            print(f"Error in {symbol}: {e}")
            continue

    # Sort and get top 10
    top_10 = results[:10]

    if top_10:
        msg = "*🔍 Angel Scanner Results:*\n\n"
        for sym, price, tag in top_10:
            msg += f"➡️ *{sym}* @ ₹{price} — `{tag}`\n"
        send_telegram_message(msg)
    else:
        send_telegram_message("⚠️ No matching stocks found at this moment.")


if __name__ == "__main__":
    scan()
