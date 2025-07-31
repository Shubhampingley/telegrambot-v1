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
    res = requests.post(url, json=payload)
    print(f"Telegram response: {res.status_code}, {res.text}")

# === Get NSE Symbols from Bhavcopy ===
def get_nse_symbols():
    today = datetime.datetime.now().strftime('%d%b%Y').upper()
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
        print(f"Bhavcopy load failed: {e}")
        return []

# === VCP Detection (Light Test Version) ===
def detect_vcp(df):
    try:
        ranges = (df['High'] - df['Low']).tail(5)
        volumes = df['Volume'].tail(5)

        # Less strict: only check last 2 ranges and volumes
        contracting = ranges.iloc[-3] > ranges.iloc[-2] > ranges.iloc[-1]
        volume_contracting = volumes.iloc[-3] > volumes.iloc[-2] > volumes.iloc[-1]

        breakout = df['Close'].iloc[-1] > df['High'].iloc[-4:-1].max()

        return contracting and volume_contracting and breakout
    except Exception as e:
        print(f"VCP logic failed: {e}")
        return False

# === Main Scanner ===
symbols = get_nse_symbols()
if not symbols:
    symbols = []

# Always include fallback stock for testing
test_stock = "TATAPOWER.NS"
if test_stock not in symbols:
    symbols.append(test_stock)

print(f"Scanning {len(symbols)} stocks...")

for symbol in symbols:
    try:
        df = yf.download(symbol, period="10d", interval="1d", progress=False)
        if len(df) < 7:
            continue

        matches = []

        if detect_vcp(df):
            matches.append("VCP")

        if matches:
            msg = f"📈 {symbol} match:\n" + " + ".join(matches)
            print(msg)
            send_telegram(msg)

    except Exception as e:
        print(f"{symbol} failed: {e}")
