import os, time, requests, pyotp
from telegram import Bot

# ─── Load Secrets ─────────────────────────────────────────────────────────────
TELEGRAM_TOKEN    = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID  = os.getenv("TELEGRAM_CHAT_ID")
ANGEL_API_KEY     = os.getenv("ANGEL_API_KEY")
ANGEL_CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
ANGEL_MPIN        = os.getenv("ANGEL_MPIN")
ANGEL_TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

bot = Bot(token=TELEGRAM_TOKEN)

def send(msg):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

# ─── MPIN Login ────────────────────────────────────────────────────────────────
def mpin_login():
    totp = pyotp.TOTP(ANGEL_TOTP_SECRET).now()
    url = "https://apiconnect.angelbroking.com/rest/secure/angelbroking/userauth/v1/loginByPin"
    headers = {
        "X-API-Key": ANGEL_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "clientcode": ANGEL_CLIENT_CODE,
        "mpin": ANGEL_MPIN,
        "totp": totp
    }
    resp = requests.post(url, json=payload, headers=headers).json()
    send(f"🔍 LOGIN RESPONSE:\n{resp}")
    if not resp.get("status"):
        raise Exception(resp.get("message"))
    return resp["data"]["jwtToken"]

# ─── Fetch LTP Data ────────────────────────────────────────────────────────────
def fetch_market(jwt_token):
    # For a full scanner you'd loop through all symbol/token pairs.
    SYMBOLS = {
      "RELIANCE": "2885",
      "TCS": "11536",
      "INFY": "1594"
    }
    url = "https://apiconnect.angelbroking.com/rest/secure/angelbroking/market/v1/getLtpData"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "X-API-Key": ANGEL_API_KEY,
        "Content-Type": "application/json"
    }

    rows = []
    for sym, token in SYMBOLS.items():
        body = {
          "exchange": "NSE",
          "symboltoken": token,
          "tradingsymbol": sym,
          "clientcode": ANGEL_CLIENT_CODE
        }
        r = requests.post(url, json=body, headers=headers).json()
        data = r.get("data") or {}
        rows.append((sym, data.get("ltp"), data.get("volume")))
        time.sleep(0.2)
    return rows

# ─── Main Scan ────────────────────────────────────────────────────────────────
def scan():
    try:
        jwt_token = mpin_login()
        send("✅ MPIN Login OK — Starting scan")

        market = fetch_market(jwt_token)
        # Top 5 by volume:
        top_vol = sorted([r for r in market if r[2]], key=lambda x: x[2], reverse=True)[:5]

        msg = "🔥 Top 5 Volume Stocks:\n" + "\n".join(
            f"{s} — ₹{p} | Vol:{v}" for s,p,v in top_vol
        )
        send(msg)

    except Exception as e:
        send(f"❌ Scanner Error: {e}")

if __name__ == "__main__":
    scan()
