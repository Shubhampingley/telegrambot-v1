import os
import pyotp
import requests
from SmartApi.smartConnect import SmartConnect

# ─── Configuration ──────────────────────────────────────────────────────────────
API_KEY       = os.getenv("ANGEL_API_KEY")
CLIENT_CODE   = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD      = os.getenv("ANGEL_PASSWORD")    # your M-PIN
TOTP_SECRET   = os.getenv("ANGEL_TOTP_SECRET")
TELE_TOKEN    = os.getenv("TELEGRAM_TOKEN")
TELE_CHAT_ID  = os.getenv("TELEGRAM_CHAT_ID")

# ─── Quick Env-Var Debug ─────────────────────────────────────────────────────────
def send_telegram(msg: str):
    url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    payload = {"chat_id": TELE_CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload)
    except:
        pass

# Send a masked debug line about M-PIN presence
pin_present = bool(PASSWORD)
pin_len = len(PASSWORD) if PASSWORD else 0
send_telegram(f"DEBUG: ANGEL_PASSWORD present? {pin_present}, length={pin_len}")

if not PASSWORD:
    send_telegram("❌ ANGEL_PASSWORD (your M-PIN) is empty or unset!")
    exit(1)

# ─── Rest of your code remains the same ───────────────────────────────────────────
def angel_login():
    try:
        obj = SmartConnect(api_key=API_KEY)
        totp = pyotp.TOTP(TOTP_SECRET).now()
        resp = obj.generateSession(
            clientCode=CLIENT_CODE,
            password=PASSWORD,
            totp=totp
        )
        send_telegram(f"DEBUG Login response:\n```{resp}```")
        # ...etc
