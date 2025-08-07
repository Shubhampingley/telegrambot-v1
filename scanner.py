import os
import pyotp
import requests
from SmartApi.smartConnect import SmartConnect

API_KEY     = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
M_PIN       = os.getenv("ANGEL_PASSWORD")     # your M-PIN
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")
TG_TOKEN    = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID  = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": text}
    try:
        r = requests.post(url, data=payload)
        print("Telegram:", r.status_code, r.text)
    except Exception as e:
        print("Telegram error:", e)

def main():
    # 1) Test Angel login
    try:
        client = SmartConnect(api_key=API_KEY)
        totp = pyotp.TOTP(TOTP_SECRET).now()
        resp = client.generateSession(clientCode=CLIENT_CODE, password=M_PIN, totp=totp)
        if resp and resp.get("data", None):
            send_telegram("✅ Angel API login successful — Telegram is working!")
        else:
            send_telegram(f"❌ Angel login failed (no data):\n{resp}")
    except Exception as e:
        send_telegram(f"❌ Angel login exception:\n{e}")

if __name__ == "__main__":
    main()
