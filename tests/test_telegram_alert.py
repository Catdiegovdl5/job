import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("Error: TELEGRAM_TOKEN or TELEGRAM_CHAT_ID not found in .env")
    exit(1)

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": "🚨 TEST ALERT: Connectivity Verified."
}

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
