import os
import pyotp
import requests
from telegram import Bot

# ─── Load your secrets from environment variables ─────────────────────────
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
    # 1. Generate TOTP
    totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()

    # 2. Call Angel One MPIN login endpoint
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

    resp = requests.post(url, json=payload, headers=headers).json()

    # 3. Send the raw response to Telegram for visibility
    send(f"🔍 Angel Login Response:\n{resp}")

    # 4. Confirm success or failure
    if resp.get("status") and resp["data"].get("jwtToken"):
        send("✅ Test Successful: Angel MPIN login + Telegram are working!")
    else:
        send("❌ Test Failed: Check Angel credentials/TOTP.")

if __name__ == "__main__":
    test_login_and_telegram()
