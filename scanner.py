import os
import pyotp
import requests
from SmartApi.smartConnect import SmartConnect
from telegram import Bot

# --- Load Secrets from Environment Variables ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ANGEL_API_KEY = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_PASSWORD = os.getenv("ANGEL_PASSWORD")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

# --- Check if any secret is missing ---
required_vars = {
    "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
    "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
    "ANGEL_API_KEY": ANGEL_API_KEY,
    "ANGEL_CLIENT_CODE": ANGEL_CLIENT_CODE,
    "ANGEL_PASSWORD": ANGEL_PASSWORD,
    "ANGEL_TOTP_SECRET": ANGEL_TOTP_SECRET,
}

missing = [key for key, value in required_vars.items() if not value]
if missing:
    raise Exception(f"❌ Missing required secrets: {', '.join(missing)}")

# --- Generate TOTP ---
totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()

# --- Login to Angel One and Notify on Telegram ---
try:
    obj = SmartConnect(api_key=ANGEL_API_KEY)
    data = obj.generateSession(ANGEL_CLIENT_CODE, ANGEL_PASSWORD, totp)

    refresh_token = data["data"]["refreshToken"]
    feed_token = obj.getfeedToken()
    profile = obj.getProfile(refresh_token)

    # --- Success Message ---
    msg = f"✅ Angel Login Successful!\nUser: {profile['data']['name']}"
    Bot(token=TELEGRAM_TOKEN).send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

except Exception as e:
    # --- Error Message ---
    error_msg = f"❌ Angel Login Failed:\n{str(e)}"
    Bot(token=TELEGRAM_TOKEN).send_message(chat_id=TELEGRAM_CHAT_ID, text=error_msg)
    raise
