import pyotp
import requests
import json

# --- 🔐 Your Angel One Credentials ---
client_code = "s149695"
password = "Shubham@123"
api_key = "GMi3vJVL"
api_secret = "55e67a16-9191-4b1b-91ab-6236f0f3dda5"
totp_secret = "TDUDCO7UVUUMP3RATR2BL3WHVY"

# --- ⏱️ Generate TOTP ---
totp = pyotp.TOTP(totp_secret).now()
print("TOTP Code:", totp)

# --- 📦 API Request Payload ---
url = "https://apiconnect.angelbroking.com/rest/auth/angelbroking/user/v1/loginByPassword"

payload = {
    "clientcode": client_code,
    "password": password,
    "totp": totp
}

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-UserType": "USER",
    "X-SourceID": "WEB",
    "X-ClientLocalIP": "127.0.0.1",
    "X-ClientPublicIP": "127.0.0.1",
    "X-MACAddress": "00:00:00:00:00:00",
    "X-PrivateKey": api_key
}

# --- 🚀 Send Login Request ---
response = requests.post(url, json=payload, headers=headers)

# --- 🧪 Debug API Response ---
try:
    data = response.json()
except Exception as e:
    print("❌ Error making API request:", e)
    print("🔍 Raw response content:")
    print(response.text)
    exit()

# --- ✅ Check Login Success ---
if data.get("status") == True:
    token = data["data"]["jwtToken"]
    print("✅ Login successful!")
    with open("angel_token.txt", "w") as f:
        f.write(token)
    print("🔐 Token saved to angel_token.txt")
else:
    print("❌ Login failed. Response:")
    print(json.dumps(data, indent=2))
