import pyotp
import requests
import json

# ---- Angel SmartAPI Credentials ----
client_code = "s149695"
api_key = "GMi3vJVL"
api_secret = "55e67a16-9191-4b1b-91ab-6236f0f3dda5"
totp_secret = "TDUDCO7UVUUMP3RATR2BL3WHVY"
password = "Shubham@123"

# ---- Generate TOTP ----
totp = pyotp.TOTP(totp_secret)
totp_code = totp.now()

# ---- Login API ----
url = "https://apiconnect.angelbroking.com/rest/auth/angelbroking/user/v1/loginByPassword"
headers = {
    "Content-Type": "application/json",
    "X-ClientLocalIP": "127.0.0.1",
    "X-ClientPublicIP": "127.0.0.1",
    "X-MACAddress": "AA:BB:CC:DD:EE:FF",
    "X-PrivateKey": api_key
}

payload = {
    "clientcode": client_code,
    "password": password,
    "totp": totp_code
}

response = requests.post(url, headers=headers, data=json.dumps(payload))
data = response.json()

if data.get("status") == True:
    token = data["data"]["jwtToken"]
    print("✅ Login successful. Token:\n", token)
    
    # Save token to file
    with open("angel_token.txt", "w") as f:
        f.write(token)
else:
    print("❌ Login failed:", data.get("message"))
