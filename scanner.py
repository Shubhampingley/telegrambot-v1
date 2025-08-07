import os
import pyotp
import time
import requests
from SmartApi.smartConnect import SmartConnect

# Load secrets
API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
MPIN = os.getenv("ANGEL_MPIN")
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message: str):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        res = requests.post(url, data=payload)
        print("Telegram status:", res.status_code)
    except Exception as e:
        print("Telegram error:", e)

def generate_totp(secret):
    return pyotp.TOTP(secret).now()

def angel_login():
    try:
        smartApi = SmartConnect(api_key=API_KEY)
        totp = generate_totp(TOTP_SECRET)
        data = smartApi.generateSession(CLIENT_CODE, MPIN, totp)

        if "data" in data and "accessToken" in data["data"]:
            smartApi.setAccessToken(data["data"]["accessToken"])
            send_telegram_message("✅ Angel API login successful — Token generated!")
            return smartApi
        else:
            send_telegram_message(f"❌ Login Failed\n{data}")
            print(data)
            return None
    except Exception as e:
        send_telegram_message(f"❌ Exception during login: {e}")
        print("Login error:", e)
        return None

def fetch_sample_ltp(smartApi):
    try:
        ltp = smartApi.ltpData(exchange="NSE", tradingsymbol="SBIN-EQ", symboltoken="3045")
        if ltp and ltp.get("data"):
            price = ltp["data"]["ltp"]
            send_telegram_message(f"✅ SBIN LTP: ₹{price}")
        else:
            send_telegram_message(f"⚠️ LTP fetch failed\n{ltp}")
    except Exception as e:
        send_telegram_message(f"❌ Error fetching LTP: {e}")
        print("LTP error:", e)

def main():
    smartApi = angel_login()
    if smartApi:
        fetch_sample_ltp(smartApi)

if __name__ == "__main__":
    main()
