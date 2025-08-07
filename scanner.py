import os
import pyotp
import requests
from SmartApi.smartConnect import SmartConnect

# ─── Config ─────────────────────────────────────────────────────────────────────
API_KEY     = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
M_PIN       = os.getenv("ANGEL_PASSWORD")     # your M-PIN
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")
TG_TOKEN    = os.getenv("TELEGRAM_TOKEN")
TG_CHAT_ID  = os.getenv("TELEGRAM_CHAT_ID")

# ─── Helpers ────────────────────────────────────────────────────────────────────
def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": text}
    try:
        r = requests.post(url, data=payload)
        print("Telegram:", r.status_code, r.text)
    except Exception as e:
        print("Telegram error:", e)

# ─── Main ───────────────────────────────────────────────────────────────────────
def main():
    # 1) Login
    client = SmartConnect(api_key=API_KEY)
    totp   = pyotp.TOTP(TOTP_SECRET).now()
    resp   = client.generateSession(clientCode=CLIENT_CODE, password=M_PIN, totp=totp)
    access = resp.get("data", {}).get("accessToken")
    client.setAccessToken(access)

    # 2) Fetch LTP for RELIANCE
    #    First search to get token
    search = client.searchScrip("NSE", "RELIANCE")
    token  = search["data"]["token"]
    ltp    = client.ltpData("NSE", token)["data"]["ltp"]

    # 3) Send result
    send_telegram(f"📈 RELIANCE LTP: ₹{ltp}")

if __name__ == "__main__":
    main()
