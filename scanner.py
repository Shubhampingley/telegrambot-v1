import os
from telegram import Bot
from SmartApi import SmartConnect
import pyotp
import time

# Load from environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ANGEL_API_KEY = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_PASSWORD = os.getenv("ANGEL_PASSWORD")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram_message(msg):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

def angel_login():
    obj = SmartConnect(api_key=ANGEL_API_KEY)
    totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
    data = obj.generateSession(ANGEL_CLIENT_CODE, ANGEL_PASSWORD, totp)
    if not data.get("status") == True:
        raise Exception("Login failed")
    return obj

def test_fetch_data():
    try:
        obj = angel_login()
        stocks = ["RELIANCE-EQ", "TCS-EQ", "HDFCBANK-EQ", "INFY-EQ", "ITC-EQ"]
        msg = "🧪 *Test Prices:*\n"
        for scrip in stocks:
            params = {
                "exchange": "NSE",
                "symboltoken": obj.searchScrip("NSE", scrip)["data"][0]["token"],
                "symbol": scrip
            }
            ltp_data = obj.ltpData(params["exchange"], params["symboltoken"], params["symbol"])
            ltp = ltp_data['data']['ltp']
            msg += f"{scrip}: ₹{ltp}\n"
            time.sleep(0.5)  # slight delay to avoid rate limits
        send_telegram_message(msg)
    except Exception as e:
        send_telegram_message(f"❌ Error in Test: {str(e)}")

if __name__ == "__main__":
    test_fetch_data()
