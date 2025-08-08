import os
import pyotp
import requests
from SmartApi import SmartConnect  # ✅ Correct import
from dotenv import load_dotenv

# Load secrets from environment (GitHub Secrets or .env file)
load_dotenv()

ANGEL_API_KEY = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_PASSWORD = os.getenv("ANGEL_PASSWORD")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message):
    """Send a message to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)

def main():
    try:
        # Login to Angel One
        obj = SmartConnect(api_key=ANGEL_API_KEY)
        totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
        obj.generateSession(ANGEL_CLIENT_CODE, ANGEL_PASSWORD, totp)

        # Fetch price for RELIANCE-EQ
        data = obj.ltpData("NSE", "RELIANCE-EQ", "RELIANCE-EQ")
        price = data['data']['ltp']

        # Send price to Telegram
        send_telegram(f"RELIANCE-EQ Price: ₹{price}")
        print(f"✅ Price sent to Telegram: ₹{price}")

    except Exception as e:
        send_telegram(f"❌ Error: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
