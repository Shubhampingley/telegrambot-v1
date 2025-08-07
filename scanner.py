import os
import pyotp
import requests
from smartapi import SmartConnect
from telegram import Bot

# Load secrets from GitHub environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ANGEL_API_KEY = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_PASSWORD = os.getenv("ANGEL_PASSWORD")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

# Validate secrets
required_vars = [TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, ANGEL_API_KEY, ANGEL_CLIENT_CODE, ANGEL_PASSWORD, ANGEL_TOTP_SECRET]
if not all(required_vars):
    raise Exception("❌ Missing one or more environment variables. Please check your GitHub secrets.")

# Generate TOTP
totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()

# Angel One Login
try:
    obj = SmartConnect(api_key=ANGEL_API_KEY)
    data = obj.generateSession(ANGEL_CLIENT_CODE, ANGEL_PASSWORD, totp)
    refresh_token = data['data']['refreshToken']
    feed_token = obj.getfeedToken()
    profile = obj.getProfile(refresh_token)

    # ✅ Send Telegram confirmation
    msg = f"✅ Angel Login Successful!\nUser: {profile['data']['name']}"
    Bot(token=TELEGRAM_TOKEN).send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

except Exception as e:
    error_msg = f"❌ Angel Login Failed:\n{str(e)}"
    Bot(token=TELEGRAM_TOKEN).send_message(chat_id=TELEGRAM_CHAT_ID, text=error_msg)
    raise
