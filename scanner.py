import os
import time
import pyotp
import requests
from smartapi.smartConnect import SmartConnect

# Load secrets from environment
API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD = os.getenv("ANGEL_PASSWORD")
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        print(f"Telegram status: {response.status_code}")
    except Exception as e:
        print(f"Telegram Error: {e}")

def angel_login():
    try:
        totp = pyotp.TOTP(TOTP_SECRET).now()
        client = SmartConnect(api_key=API_KEY)
        data = client.generateSession(CLIENT_CODE, PASSWORD, totp)
        if "data" not in data or "accessToken" not in data["data"]:
            send_telegram("❌ Login Failed: 'accessToken' not received")
            print("Login failed:", data)
            return None, None
        access_token = data["data"]["accessToken"]
        client.setSessionExpiryHook(lambda: print("Session expired"))
        return client, access_token
    except Exception as e:
        send_telegram(f"❌ Exception during login: {e}")
        return None, None

def fetch_sample_ltp(client):
    try:
        # NSE NIFTY index example (symbolToken = "99926009", symbol = "NIFTY")
        resp = client.ltpData(exchange="NSE", tradingsymbol="NIFTY", symboltoken="99926009")
        if resp.get("status") and "data" in resp:
            ltp = resp["data"]["ltp"]
            send_telegram(f"✅ NIFTY LTP: {ltp}")
        else:
            send_telegram(f"⚠️ Failed to fetch LTP: {resp}")
    except Exception as e:
        send_telegram(f"❌ Error fetching LTP: {e}")

def main():
    client, token = angel_login()
    if not client:
        return
    send_telegram("✅ Angel One Login Successful")
    fetch_sample_ltp(client)

if __name__ == "__main__":
    main()
