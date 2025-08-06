import os
import pandas as pd
from datetime import datetime
from telegram import Bot
from SmartApi import SmartConnect
import pyotp

# Load from environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ANGEL_API_KEY = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_PASSWORD = os.getenv("ANGEL_PASSWORD")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

bot = Bot(token=TELEGRAM_TOKEN)

# ✅ Angel login with error handling
def angel_login():
    try:
        obj = SmartConnect(api_key=ANGEL_API_KEY)
        totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
        data = obj.generateSession(ANGEL_CLIENT_CODE, ANGEL_PASSWORD, totp)

        if not data or 'data' not in data or 'refreshToken' not in data['data']:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"❌ Angel Login Failed: Invalid credentials or TOTP.\nResponse: {data}")
            raise Exception("Login failed, check credentials and TOTP.")

        refresh_token = data['data']['refreshToken']
        obj.getProfile(refresh_token)
        return obj

    except Exception as e:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"❌ Angel Login Error: {str(e)}")
        raise

# ✅ Fetch all stocks from Angel One
def fetch_market_data(obj):
    exchange = 'NSE'
    try:
        all_stocks = obj.searchScrip(exchange, '')
        return pd.DataFrame(all_stocks['data'])
    except Exception as e:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"❌ Failed to fetch stock data: {str(e)}")
        raise

# ✅ Filter: Top 5 by volume
def get_top_volume(df):
    df = df[df['volume'] > 0]
    return df.sort_values(by='volume', ascending=False).head(5)

# ✅ Filter: Near 52-week high
def get_52_week_high(df):
    df = df[df['yearHigh'] > 0]
    df = df[df['lastPrice'] >= df['yearHigh'] * 0.98]
    return df.sort_values(by='lastPrice', ascending=False).head(5)

# ✅ Send update to Telegram
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

    if msg.strip():
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
    else:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="⚠️ No matching stocks found right now.")

# ✅ Main scan function
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
