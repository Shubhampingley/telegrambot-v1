import yfinance as yf
import requests
import datetime
import zipfile
import io
import pandas as pd
import urllib.request

# === Telegram Config ===
TELEGRAM_BOT_TOKEN = '8116462125:AAF-Nw313C1vew8Y96InHWJBXX9VnwbxFFc'
TELEGRAM_CHAT_ID = '665594180'

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload)

# === Fetch symbols from latest Bhavcopy ===
def get_nse_symbols():
    today = datetime.datetime.now().strftime('%d%b%Y').upper()  # e.g., 30JUL2025
    url = f"https://www1.nseindia.com/content/historical/EQUITIES/2025/JUL/cm{today}bhav.csv.zip"

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            zipfile_bytes = io.BytesIO(response.read())
        with zipfile.ZipFile(zipfile_bytes) as z:
            for name in z.namelist():
                if name.endswith('.csv'):
                    with z.open(name) as f:
                        df = pd.read_csv(f)
                        symbols = df['SYMBOL'].unique()
                        return [s + ".NS" for s in symbols if isinstance(s, str)]
    except Exception as e:
        print(f"Failed to load Bhavcopy: {e}")
        return []

# === Scanner Logic ===
symbols = get_nse_symbols()

for symbol in symbols:
    try:
        df = yf.download(symbol, period="5d", interval="1d", progress=False)
        if len(df) < 5:
            continue

        latest_close = df['Close'].iloc[-1]
        ema_5 = df['Close'].rolling(window=5).mean().iloc[-1]
        delta = df['Close'].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        latest_rsi = rsi.iloc[-1]

        if latest_close > ema_5 and latest_rsi < 40:
            send_telegram(f"📈 {symbol}\nPrice: ₹{latest_close:.2f}\nEMA5: ₹{ema_5:.2f}\nRSI: {latest_rsi:.2f}")

    except Exception as e:
        print(f"{symbol} failed: {e}")
