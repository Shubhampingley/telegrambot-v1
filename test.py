import os
import pyotp
import requests
from telegram import Bot

# ─── Load secrets ─────────────────────────────────────────────────────────────
TELEGRAM_TOKEN    = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID  = os.getenv("TELEGRAM_CHAT_ID")
ANGEL_API_KEY     = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_MPIN        = os.getenv("ANGEL_MPIN")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

bot = Bot(token=TELEGRAM_TOKEN)

def send(msg):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

def test_login_and_telegram():
    # 1) Generate TOTP
    totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()

    # 2) Call Angel One MPIN login endpoint
    url = "https://apiconnect.angelbroking.com/rest/secure/angelbroking/userauth/v1/loginByPin"
    headers = {
        "X-API-Key": ANGEL_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "clientcode": ANGEL_CLIENT_CODE,
        "mpin": ANGEL_MPIN,
        "totp": totp
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
    except Exception as e:
        send(f"❌ HTTP request failed: {e}")
        return

    # 3) Report HTTP status & raw body
    status = resp.status_code
    body = resp.text or "<empty>"
    send(f"🔍 HTTP {status}\n{body}")

    # 4) Try parsing JSON
    try:
        data = resp.json()
    except Exception as e:
        send(f"❌ JSON parse error: {e}")
        return

    # 5) Send JSON response summary
    send(f"🔍 Parsed JSON:\n{data}")

    # 6) Success check
    if data.get("status") and data.get("data", {}).get("jwtToken"):
        send("✅ Test Successful: MPIN login & Telegram working!")
    else:
        msg = data.get("message") or "Unknown error"
        send(f"❌ Test Failed: {msg}")

if __name__ == "__main__":
    test_login_and_telegram()
