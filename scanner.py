import os
import time
import pyotp
import requests
from SmartApi.smartConnect import SmartConnect
from dotenv import load_dotenv

# Load .env secrets
load_dotenv()

# Required ENV variables
REQUIRED_VARS = [
    "ANGEL_API_KEY", "ANGEL_CLIENT_CODE", "ANGEL_PASSWORD",
    "ANGEL_TOTP_SECRET", "TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID"
]

missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
if missing:
    raise Exception(f"Missing environment variables: {', '.join(missing)}")

# Read env vars
API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD = os.getenv("ANGEL_PASSWORD")
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram(message: str):
    try:
        res = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": message}
        )
        if not res.ok:
            print("Telegram error:", res.text)
    except Exception as e:
        print("Failed to send Telegram message:", e)


def get_totp(secret: str):
    try:
        return pyotp.TOTP(secret).now()
    except Exception as e:
        send_telegram(f"❌ TOTP generation failed: {e}")
        raise


def login_to_angel():
    try:
        obj = SmartConnect(api_key=API_KEY)
        totp = get_totp(TOTP_SECRET)
        data = obj.generateSession(CLIENT_CODE, PASSWORD, totp)
        if "data" not in data or "jwtToken" not in data["data"]:
            send_telegram("❌ Login failed. Invalid credentials or TOTP.")
            raise Exception("Login failed.")
        return obj
    except Exception as e:
        send_telegram(f"❌ Angel Login failed: {e}")
        raise


def test_stock_fetch(api):
    try:
        result = api.getLTPData("NSE", "RELIANCE-EQ")
        ltp = result["data"]["ltp"]
        send_telegram(f"✅ Angel API Test Success:\nRELIANCE LTP: ₹{ltp}")
    except Exception as e:
        send_telegram(f"❌ Failed to fetch LTP: {e}")
        raise


if __name__ == "__main__":
    try:
        angel_api = login_to_angel()
        test_stock_fetch(angel_api)
    except Exception as e:
        print("Error:", e)
        send_telegram(f"❌ Critical Error: {e}")
