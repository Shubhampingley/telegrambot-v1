import os
import requests
from telegram import Bot

# Load secrets from GitHub Actions
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ANGEL_API_KEY = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")

# Example static Angel One auth token (in production, automate this via login flow)
ANGEL_AUTH_TOKEN = os.getenv("ANGEL_AUTH_TOKEN")  # This should be set via secrets

BASE_URL = "https://apiconnect.angelbroking.com/rest/secure/angelbroking/market/v1"

headers = {
    "X-PrivateKey": ANGEL_API_KEY,
    "X-ClientLocalIP": "127.0.0.1",
    "X-ClientPublicIP": "127.0.0.1",
    "X-MACAddress": "00:00:00:00:00:00",
    "X-UserType": "USER",
    "X-SourceID": "WEB",
    "Accept": "application/json",
    "X-ClientCode": ANGEL_CLIENT_CODE,
    "Authorization": f"Bearer {ANGEL_AUTH_TOKEN}"
}

def send_telegram_message(message):
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')
    except Exception as e:
        print(f"Telegram Error: {e}")

def get_market_data():
    try:
        # List of sample stock symbols (replace with full NSE list if needed)
        symbols = ["RELIANCE-EQ", "INFY-EQ", "TCS-EQ", "SBIN-EQ", "HDFCBANK-EQ", "ICICIBANK-EQ"]
        results = []

        for symbol in symbols:
            payload = {
                "exchange": "NSE",
                "symboltoken": "",  # Required if using quote endpoint (need mapping)
                "tradingsymbol": symbol
            }

            r = requests.post(f"{BASE_URL}/quote", headers=headers, json=payload)
            data = r.json()

            if "data" in data:
                results.append({
                    "symbol": symbol,
                    "ltp": data["data"].get("ltp"),
                    "dayHigh": data["data"].get("high"),
                    "dayLow": data["data"].get("low"),
                    "volume": data["data"].get("volume"),
                    "yearHigh": data["data"].get("yearlyhighprice"),
                    "yearLow": data["data"].get("yearlylowprice"),
                })

        return results

    except Exception as e:
        print(f"Error fetching market data: {e}")
        return []

def scan():
    stocks = get_market_data()
    if not stocks:
        send_telegram_message("⚠️ No market data available.")
        return

    # Filters
    week_high_hits = sorted([s for s in stocks if s["ltp"] and s["yearHigh"] and s["ltp"] >= s["yearHigh"] * 0.98], key=lambda x: x["ltp"], reverse=True)[:10]
    volume_hits = sorted([s for s in stocks if s["volume"]], key=lambda x: x["volume"], reverse=True)[:10]
    day_high_hits = sorted([s for s in stocks if s["ltp"] and s["dayHigh"] and s["ltp"] >= s["dayHigh"] * 0.98], key=lambda x: x["ltp"], reverse=True)[:10]
    day_low_hits = sorted([s for s in stocks if s["ltp"] and s["dayLow"] and s["ltp"] <= s["dayLow"] * 1.02], key=lambda x: x["ltp"])[:10]

    msg = "<b>📊 Auto Stock Scanner Results:</b>\n\n"

    def format_stocks(title, data):
        if not data:
            return f"<b>{title}</b>\nNo stocks found.\n\n"
        lines = [f"{i+1}. <b>{s['symbol']}</b> @ ₹{s['ltp']}" for i, s in enumerate(data)]
        return f"<b>{title}</b>\n" + "\n".join(lines) + "\n\n"

    msg += format_stocks("🚀 Near 52-Week Highs", week_high_hits)
    msg += format_stocks("🔥 Top Volumes", volume_hits)
    msg += format_stocks("📈 Day Highs", day_high_hits)
    msg += format_stocks("📉 Day Lows", day_low_hits)

    send_telegram_message(msg)

if __name__ == "__main__":
    scan()
