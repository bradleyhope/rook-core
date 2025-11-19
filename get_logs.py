"""
Get Render deployment logs
"""

import requests

RENDER_API_KEY = "rnd_9gdSQ9VFF1ChnMU5qu9Op9k4JQKx"
SERVICE_ID = "srv-d4f03la4d50c73e4lt7g"

headers = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
}

# Get service logs (runtime logs)
print("📋 Getting service logs...")
logs_response = requests.get(
    f"https://api.render.com/v1/services/{SERVICE_ID}/logs",
    headers=headers
)

if logs_response.status_code == 200:
    print(logs_response.text)
else:
    print(f"Error: {logs_response.status_code}")
    print(logs_response.text)
