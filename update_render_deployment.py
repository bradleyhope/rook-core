"""
Update Render deployment to use chat_server_v2.py
"""

import requests
import json

RENDER_API_KEY = "rnd_9gdSQ9VFF1ChnMU5qu9Op9k4JQKx"
SERVICE_ID = "srv-d4f03la4d50c73e4lt7g"

headers = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Content-Type": "application/json"
}

# Update service to use chat_server_v2.py
update_payload = {
    "startCommand": "cd api && uvicorn chat_server_v2:app --host 0.0.0.0 --port $PORT"
}

print("🚀 Updating Render service to use consciousness architecture...")
print(f"Service ID: {SERVICE_ID}")

response = requests.patch(
    f"https://api.render.com/v1/services/{SERVICE_ID}",
    headers=headers,
    json=update_payload
)

if response.status_code == 200:
    print("✅ Service updated successfully!")
    print(json.dumps(response.json(), indent=2))
else:
    print(f"❌ Error updating service: {response.status_code}")
    print(response.text)

# Trigger a new deploy
print("\n🔄 Triggering new deployment...")

deploy_response = requests.post(
    f"https://api.render.com/v1/services/{SERVICE_ID}/deploys",
    headers=headers,
    json={"clearCache": "clear"}
)

if deploy_response.status_code in [200, 201]:
    print("✅ Deployment triggered!")
    deploy_data = deploy_response.json()
    print(f"Deploy ID: {deploy_data.get('id')}")
    print(f"Status: {deploy_data.get('status')}")
else:
    print(f"❌ Error triggering deployment: {deploy_response.status_code}")
    print(deploy_response.text)
