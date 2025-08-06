import os
import pandas as pd
from datetime import datetime
from telegram import Bot
from SmartApi import SmartConnect
import pyotp

# Load secrets from environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ANGEL_API_KEY = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_PASSWORD = os.getenv("ANGEL_PASSWORD")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

# Telegram bot setup
bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram_message(message):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        print(f"Failed to send message to Telegram: {str(e)}")

# Login to Angel One SmartAPI
def angel_login():
    try:
        obj = SmartConnect(api_key=ANGEL_API_KEY)
        totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
        data = obj.generateSession(ANGEL_CLIENT_CODE, ANGEL_PASSWORD, totp)

        if not data or "data" not in data:
            raise Exception("❌ Login failed: Invalid session response")

        refresh_token = data["data"].get("refreshToken")
        if not refresh_token:
            raise Exception("❌ Login failed: Missing refreshToken")

        profile = obj.getProfile(refresh_token)
        if not profile or "data" not in profile:
            raise Exception("❌ Login failed: Profile fetch failed")

        return obj

    except Exception as e:
        send_telegram_message(f"❌ Angel Login Error: {str(e)}")
        raise

# Fetch all NSE stocks
def fetch_market_data(obj):
    try:
        response = obj.searchScrip('NSE', '')
        if not response or "data" not in response:
            raise Exception("❌ Failed to fetch stock data")
        return pd.DataFrame(response["data"])
    except Exception as e:
        send_telegram_message(f"❌ Fetch Market Data Error: {str(e)}")
        raise

# Filter top 5 volume stocks
def get_top_volume(df):
    df = df[df['volume'] > 0]
    return df.sort_values(by='volume', ascending=False).head(5)

# Filter top 5 near 52-week high
def get_52_week_high(df):
    df = df[df['yearHigh'] > 0]
    df = df[df['lastPrice'] >= df['yearHigh'] * 0.98]
    return df.sort_values(by='lastPrice', ascending=False).head(5)

# Send Telegram message with results
def send_results(data):
    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    message = f"📊 *Market Scan* — {now}\n"

    if not data['vol'].empty:
        message += "\n🔥 *Top 5 Volume Stocks:*\n"
        for _, row in data['vol'].iterrows():
            message += f"🔹 {row['symbol']} — ₹{row['lastPrice']} | Vol: {row['volume']}\n"

    if not data['high'].empty:
        message += "\n📈 *Near 52-Week High:*\n"
        for _, row in data['high'].iterrows():
            message += f"🚀 {row['symbol']} — ₹{row['lastPrice']} | 52WH: ₹{row['yearHigh']}\n"

    send_telegram_message(message)

# Main scan function
def scan():
    try:
        obj = angel_login()
        df = fetch_market_data(obj)
        result = {
            "vol": get_top_volume(df),
            "high": get_52_week_high(df)
        }

        if result['vol'].empty and result['high'].empty:
            send_telegram_message("⚠️ No matching stocks found at this moment.")
        else:
            send_results(result)

    except Exception as e:
        send_telegram_message(f"❌ Error in Scanner: {str(e)}")

if __name__ == "__main__":
    scan()
