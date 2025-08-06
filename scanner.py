import os
import pandas as pd
from datetime import datetime
from telegram import Bot
from SmartApi import SmartConnect
import pyotp

# Load environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ANGEL_API_KEY = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_PASSWORD = os.getenv("ANGEL_PASSWORD")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

# Setup Telegram Bot
bot = Bot(token=TELEGRAM_TOKEN)


def send_telegram_message(message):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        print(f"Telegram Error: {e}")


# Angel Login
def angel_login():
    try:
        obj = SmartConnect(api_key=ANGEL_API_KEY)
        totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
        data = obj.generateSession(ANGEL_CLIENT_CODE, ANGEL_PASSWORD, totp)

        if not data or not isinstance(data, dict) or 'data' not in data:
            raise Exception(f"Invalid login response: {data}")

        refresh_token = data['data'].get('refreshToken')
        if not refresh_token:
            raise Exception("Missing refresh token in login response")

        obj.getProfile(refresh_token)
        return obj

    except Exception as e:
        send_telegram_message(f"❌ Angel Login Error: {str(e)}")
        raise


# Fetch market data
def fetch_market_data(obj):
    exchange = 'NSE'
    response = obj.searchScrip(exchange, '')
    if not response or 'data' not in response or response['data'] is None:
        raise Exception("Failed to fetch stock data from Angel")
    return pd.DataFrame(response['data'])


# Get top 5 volume stocks
def get_top_volume(df):
    df = df[df['volume'] > 0]
    return df.sort_values(by='volume', ascending=False).head(5)


# Get stocks near 52-week high
def get_52_week_high(df):
    df = df[df['yearHigh'] > 0]
    df = df[df['lastPrice'] >= df['yearHigh'] * 0.98]
    return df.sort_values(by='lastPrice', ascending=False).head(5)


# Main scan and message
def scan():
    try:
        obj = angel_login()
        df = fetch_market_data(obj)

        top_volume = get_top_volume(df)
        top_52wh = get_52_week_high(df)

        message = f"📊 Market Scan — {datetime.now().strftime('%d-%b %H:%M:%S')}\n"

        if not top_volume.empty:
            message += "\n🔥 Top 5 Volume Stocks:\n"
            for _, row in top_volume.iterrows():
                message += f"• {row['symbol']} – ₹{row['lastPrice']} | Vol: {row['volume']}\n"
        else:
            message += "\nNo volume data found.\n"

        if not top_52wh.empty:
            message += "\n📈 Near 52-Week High:\n"
            for _, row in top_52wh.iterrows():
                message += f"• {row['symbol']} – ₹{row['lastPrice']} (52WH: ₹{row['yearHigh']})\n"
        else:
            message += "\nNo 52WH stocks found.\n"

        send_telegram_message(message)

    except Exception as e:
        send_telegram_message(f"❌ Error in Scanner: {str(e)}")


if __name__ == "__main__":
    scan()
