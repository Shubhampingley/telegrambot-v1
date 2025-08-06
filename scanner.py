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

# Telegram bot
bot = Bot(token=TELEGRAM_TOKEN)

# Angel One login
def angel_login():
    try:
        obj = SmartConnect(api_key=ANGEL_API_KEY)
        totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
        data = obj.generateSession(ANGEL_CLIENT_CODE, ANGEL_PASSWORD, totp)
        refresh_token = data['data']['refreshToken']
        obj.getProfile(refresh_token)
        return obj
    except Exception as e:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"❌ Angel Login Failed: {str(e)}")
        raise

# Fetch all NSE stock data
def fetch_stocks(obj):
    try:
        data = obj.searchScrip('NSE', '')
        return pd.DataFrame(data['data'])
    except Exception as e:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"❌ Fetch Failed: {str(e)}")
        raise

# 52-week high logic
def get_52_week_high(df):
    df = df[df['yearHigh'] > 0]
    df = df[df['lastPrice'] >= df['yearHigh'] * 0.98]
    return df.sort_values(by='lastPrice', ascending=False).head(5)

# Top volume stocks
def get_top_volume(df):
    df = df[df['volume'] > 0]
    return df.sort_values(by='volume', ascending=False).head(5)

# Telegram send
def send_to_telegram(data):
    now = datetime.now().strftime('%d-%m %H:%M')
    msg = f"📊 *Live Market Scan* — {now}\n\n"

    if not data['vol'].empty:
        msg += "🔥 *Top 5 Volume Stocks:*\n"
        for i, row in data['vol'].iterrows():
            msg += f"{row['symbol']} – ₹{row['lastPrice']} | Vol: {row['volume']}\n"

    if not data['high'].empty:
        msg += "\n📈 *52-Week High Breakouts:*\n"
        for i, row in data['high'].iterrows():
            msg += f"{row['symbol']} – ₹{row['lastPrice']} (52WH: ₹{row['yearHigh']})\n"

    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg, parse_mode="Markdown")

# Main scanner
def scan():
    try:
        obj = angel_login()
        df = fetch_stocks(obj)
        data = {
            'vol': get_top_volume(df),
            'high': get_52_week_high(df)
        }
        send_to_telegram(data)
    except Exception as e:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"❌ Error in Scanner: {str(e)}")

if __name__ == "__main__":
    scan()
