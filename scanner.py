import os
import pandas as pd
import requests
from datetime import datetime
from telegram import Bot
from SmartApi import SmartConnect
import pyotp

# Load secrets from environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ANGEL_API_KEY = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_PASSWORD = os.getenv("ANGEL_PASSWORD")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

# Validate environment variables
if not all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, ANGEL_API_KEY, ANGEL_CLIENT_CODE, ANGEL_PASSWORD, ANGEL_TOTP_SECRET]):
    raise ValueError("❌ One or more required environment variables are missing.")

# Telegram Bot
bot = Bot(token=TELEGRAM_TOKEN)

# Angel One login
def angel_login():
    obj = SmartConnect(api_key=ANGEL_API_KEY)
    totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
    data = obj.generateSession(ANGEL_CLIENT_CODE, ANGEL_PASSWORD, totp)
    if not data.get("data"):
        raise ValueError("❌ Login failed, check your credentials and TOTP.")
    refresh_token = data['data'].get('refreshToken')
    if not refresh_token:
        raise ValueError("❌ Refresh token missing from login response.")
    obj.getProfile(refresh_token)
    return obj

# Fetch market data
def fetch_market_data(obj):
    response = obj.searchScrip("NSE", '')
    if not response.get("data"):
        raise ValueError("❌ Failed to fetch market data from Angel One.")
    return pd.DataFrame(response["data"])

# 52-week high stocks
def get_52_week_high(df):
    df = df[df['yearHigh'] > 0]
    df = df[df['lastPrice'] >= df['yearHigh'] * 0.98]  # Near 52WH
    return df.sort_values(by='lastPrice', ascending=False).head(5)

# Top volume stocks
def get_top_volume(df):
    df = df[df['volume'] > 0]
    return df.sort_values(by='volume', ascending=False).head(5)

# Send to Telegram
def send_telegram(data):
    msg = f"\n📊 Market Scan — {datetime.now().strftime('%H:%M:%S')}\n"

    if not data['vol'].empty:
        msg += "\n🔥 Top 5 Volume Stocks:\n"
        for _, row in data['vol'].iterrows():
            msg += f"{row['symbol']} – ₹{row['lastPrice']} – Vol: {row['volume']}\n"

    if not data['high'].empty:
        msg += "\n📈 52-Week High Stocks:\n"
        for _, row in data['high'].iterrows():
            msg += f"{row['symbol']} – ₹{row['lastPrice']} – 52WH: ₹{row['yearHigh']}\n"

    if "Top" not in msg:
        msg += "\n⚠️ No relevant stock updates at this moment."

    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

# Main scan
def scan():
    try:
        obj = angel_login()
        df = fetch_market_data(obj)
        data = {
            "vol": get_top_volume(df),
            "high": get_52_week_high(df)
        }
        send_telegram(data)
    except Exception as e:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"❌ Error in Scanner: {str(e)}")

if __name__ == "__main__":
    scan()
