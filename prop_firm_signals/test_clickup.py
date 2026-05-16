import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

CLICKUP_API_KEY = os.environ["CLICKUP_API_KEY"]
CLICKUP_LIST_ID = os.environ["CLICKUP_LIST_ID"]

now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

payload = {
    "name": "🔔 GOLD — LONG (HC) [TEST]",
    "description": (
        "Asset     : GOLD\n"
        "Direction : LONG\n"
        "Conviction: HC\n"
        "Entry Price: 3245.80\n"
        "TP        : 3271.04  (+$25)\n"
        "SL        : 3233.55  (-$12.50)\n"
        "RR        : 1:2.0\n"
        "RSI       : 58.5\n"
        "Volume    : Above Average\n"
        f"Signal Time: {now_utc}\n\n"
        "*** This is a test notification ***"
    ),
    "status": "to do",
}

print(f"Sending test notification to ClickUp list {CLICKUP_LIST_ID}...")

resp = requests.post(
    f"https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task",
    headers={"Content-Type": "application/json", "Authorization": CLICKUP_API_KEY},
    json=payload,
    timeout=10,
)

if resp.status_code in (200, 201):
    task = resp.json()
    print(f"✅ Task created successfully!")
    print(f"   Task ID  : {task.get('id')}")
    print(f"   Task Name: {task.get('name')}")
    print(f"   URL      : {task.get('url')}")
else:
    print(f"❌ Failed: {resp.status_code}")
    print(f"   {resp.text}")
