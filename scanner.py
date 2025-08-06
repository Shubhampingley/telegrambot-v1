import os
import pandas as pd
from datetime import datetime
from telegram import Bot
from SmartApi import SmartConnect
import pyotp

# Load ENV
TELEGRAM_TOKEN    = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID  = os.getenv("TELEGRAM_CHAT_ID")
ANGEL_API_KEY     = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_MPIN        = os.getenv("ANGEL_MPIN")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

bot = Bot(token=TELEGRAM_TOKEN)

def send_telegram_message(msg):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg, parse_mode="Markdown")
    except Exception as e:
        print("Telegram Error:", e)

def angel_login():
    api = SmartConnect(api_key=ANGEL_API_KEY)
    totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
    # Positional args here:
    resp = api.generateSession(ANGEL_CLIENT_CODE, ANGEL_MPIN, totp)
    if not resp or not resp.get("data", {}).get("refreshToken"):
        raise Exception(f"Login failed: {resp}")
    rtok = resp["data"]["refreshToken"]
    prof = api.getProfile(rtok)
    if not prof or not prof.get("data"):
        raise Exception(f"Profile fetch failed: {prof}")
    return api

def fetch_market_data(api):
    resp = api.searchScrip("NSE", "")
    if not resp or not resp.get("data"):
        raise Exception(f"Fetch failed: {resp}")
    return pd.DataFrame(resp["data"])

def get_top_volume(df):
    return df[df["volume"]>0].sort_values("volume", ascending=False).head(5)

def get_52_week_high(df):
    df = df[df["yearHigh"]>0]
    return df[df["lastPrice"]>=df["yearHigh"]*0.98].sort_values("lastPrice", ascending=False).head(5)

def scan():
    try:
        api = angel_login()
        df  = fetch_market_data(api)
        top_vol = get_top_volume(df)
        top_52  = get_52_week_high(df)

        now = datetime.now().strftime("%d-%b %H:%M")
        msg = f"📊 *Market Scan* — {now}\n\n"

        if not top_vol.empty:
            msg += "🔥 *Top 5 Volume Stocks:*\n"
            for _, r in top_vol.iterrows():
                msg += f"• {r['symbol']} — ₹{r['lastPrice']} | Vol: {r['volume']}\n"
        else:
            msg += "⚠️ No volume data.\n"

        if not top_52.empty:
            msg += "\n📈 *Near 52W High:*\n"
            for _, r in top_52.iterrows():
                msg += f"• {r['symbol']} — ₹{r['lastPrice']} (52WH: ₹{r['yearHigh']})\n"
        else:
            msg += "⚠️ No 52-week high stocks.\n"

        send_telegram_message(msg)

    except Exception as e:
        send_telegram_message(f"❌ Scanner Error: {e}")

if __name__ == "__main__":
    scan()
