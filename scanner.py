import requests
import pandas as pd
from datetime import datetime, timedelta

# Telegram Setup
BOT_TOKEN = "8116462125:AAF-Nw313C1vew8Y96InHWJBXX9VnwbxFFc"
CHAT_ID = "665594180"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Example stock list (replace with full NSE 500 list)
NSE_STOCKS = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]

def get_price_data(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}.NS?interval=1d&range=30d"
    r = requests.get(url)
    data = r.json()
    prices = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
    timestamps = data["chart"]["result"][0]["timestamp"]
    df = pd.DataFrame({"timestamp": timestamps, "close": prices})
    df["date"] = pd.to_datetime(df["timestamp"], unit="s")
    return df.dropna()

def check_crossover(df, short=9, long=21):
    df["short_ma"] = df["close"].rolling(short).mean()
    df["long_ma"] = df["close"].rolling(long).mean()
    if df["short_ma"].iloc[-2] < df["long_ma"].iloc[-2] and df["short_ma"].iloc[-1] > df["long_ma"].iloc[-1]:
        return "buy"
    if df["short_ma"].iloc[-2] > df["long_ma"].iloc[-2] and df["short_ma"].iloc[-1] < df["long_ma"].iloc[-1]:
        return "sell"
    return None

def send_telegram_message(message):
    requests.post(TELEGRAM_API, data={"chat_id": CHAT_ID, "text": message})

def main():
    for symbol in NSE_STOCKS:
        try:
            df = get_price_data(symbol)
            signal = check_crossover(df)
            if signal:
                msg = f"📈 {symbol} generated a {signal.upper()} signal at ₹{df['close'].iloc[-1]:.2f}"
                print(msg)
                send_telegram_message(msg)
        except Exception as e:
            print(f"Error checking {symbol}: {e}")

if __name__ == "__main__":
    main()
