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

# Telegram Bot
bot = Bot(token=TELEGRAM_TOKEN)

# Angel One login
def angel_login():
    obj = SmartConnect(api_key=ANGEL_API_KEY)
    totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
    data = obj.generateSession(ANGEL_CLIENT_CODE, ANGEL_PASSWORD, totp)
    refresh_token = data['data']['refreshToken']
    user_profile = obj.getProfile(refresh_token)
    return obj

# Fetch market data
def fetch_market_data(obj):
    exchange = 'NSE'
    all_stocks = obj.searchScrip(exchange, '')
    return pd.DataFrame(all_stocks['data'])

# 52-week high stocks
def get_52_week_high(df):
    df = df[df['yearHigh'] > 0]  # Filter valid
    df = df[df['lastPrice'] >= df['yearHigh'] * 0.98]  # Near 52WH
    top_52wh = df.sort_values(by='lastPrice', ascending=False).head(5)
    return top_52wh

# Top volume stocks
def get_top_volume(df):
    df = df[df['volume'] > 0]
    top_vol = df.sort_values(by='volume', ascending=False).head(5)
    return top_vol

# Send to Telegram
def send_telegram(data):
    msg = f"\n📊 Market Scan — {datetime.now().strftime('%H:%M:%S')}\n"

    if not data['vol'].empty:
        msg += "\n🔥 Top 5 Volume Stocks:\n"
        for i, row in data['vol'].iterrows():
            msg += f"{row['symbol']} – ₹{row['lastPrice']} – Vol: {row['volume']}\n"

    if not data['high'].empty:
        msg += "\n📈 52-Week High Stocks:\n"
        for i, row in data['high'].iterrows():
            msg += f"{row['symbol']} – ₹{row['lastPrice']} – 52WH: ₹{row['yearHigh']}\n"

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
