import os, time, requests, pyotp
from telegram import Bot
from datetime import datetime

# Load secrets
TELEGRAM_TOKEN    = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID  = os.getenv("TELEGRAM_CHAT_ID")
ANGEL_API_KEY     = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_MPIN        = os.getenv("ANGEL_MPIN")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

bot = Bot(token=TELEGRAM_TOKEN)

def send(msg):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg, parse_mode="Markdown")

def mpin_login():
    totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
    url = "https://apiconnect.angelbroking.com/rest/secure/angelbroking/userauth/v1/loginByPin"
    headers = {"X-API-Key": ANGEL_API_KEY, "Content-Type": "application/json"}
    payload = {"clientcode": ANGEL_CLIENT_CODE, "mpin": ANGEL_MPIN, "totp": totp}
    resp = requests.post(url, json=payload, headers=headers).json()
    if not resp.get("status"):
        raise Exception(resp.get("message"))
    return resp["data"]["jwtToken"]

def fetch_market(jwt_token):
    SYMBOLS = {"RELIANCE":"2885","TCS":"11536","INFY":"1594"}  # expand as needed
    url = "https://apiconnect.angelbroking.com/rest/secure/angelbroking/market/v1/getLtpData"
    headers = {"Authorization": f"Bearer {jwt_token}", "X-API-Key": ANGEL_API_KEY}
    rows = []
    for sym, token in SYMBOLS.items():
        body = {"exchange":"NSE","symboltoken":token,"tradingsymbol":sym,"clientcode":ANGEL_CLIENT_CODE}
        r = requests.post(url, json=body, headers=headers).json()
        data = r.get("data", {})
        rows.append((sym, data.get("ltp",0), data.get("volume",0)))
        time.sleep(0.2)
    return rows

def scan():
    try:
        jwt = mpin_login()
        send("✅ MPIN Login OK — Starting scan")
        market = fetch_market(jwt)
        top_vol = sorted(market, key=lambda x: x[2], reverse=True)[:5]
        now = datetime.now().strftime("%d-%b %H:%M")
        msg = f"📊 *Market Scan* — {now}\n\n🔥 *Top 5 Volume Stocks:*\n"
        for s,p,v in top_vol:
            msg += f"• {s} — ₹{p} | Vol:{v}\n"
        send(msg)
    except Exception as e:
        send(f"❌ Scanner Error: {e}")

if __name__=="__main__":
    scan()
