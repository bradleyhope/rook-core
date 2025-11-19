"""
Check Render deployment status and recent logs
"""

import requests
import json

RENDER_API_KEY = "rnd_9gdSQ9VFF1ChnMU5qu9Op9k4JQKx"
SERVICE_ID = "srv-d4f03la4d50c73e4lt7g"

headers = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Content-Type": "application/json"
}

# Get service details
print("📊 Checking service status...")
service_response = requests.get(
    f"https://api.render.com/v1/services/{SERVICE_ID}",
    headers=headers
)

if service_response.status_code == 200:
    service = service_response.json()
    print(f"Service: {service['name']}")
    print(f"Status: {service.get('suspended', 'unknown')}")
    print(f"URL: {service['serviceDetails']['url']}")
else:
    print(f"Error getting service: {service_response.status_code}")
    print(service_response.text)

# Get recent deploys
print("\n📦 Recent deployments...")
deploys_response = requests.get(
    f"https://api.render.com/v1/services/{SERVICE_ID}/deploys",
    headers=headers
)

if deploys_response.status_code == 200:
    deploys_data = deploys_response.json()
    print(f"Response: {json.dumps(deploys_data, indent=2)[:500]}")
    
    deploys = deploys_data if isinstance(deploys_data, list) else deploys_data.get('deploys', [])
    
    for deploy in deploys[:3]:  # Last 3 deploys
        deploy_id = deploy.get('deploy', {}).get('id') or deploy.get('id')
        print(f"\nDeploy ID: {deploy_id}")
        print(f"  Status: {deploy.get('status', 'unknown')}")
        print(f"  Created: {deploy.get('createdAt', 'unknown')}")
        if deploy.get('finishedAt'):
            print(f"  Finished: {deploy['finishedAt']}")
        
        # Get logs for this deploy
        if deploy.get('status') in ['build_failed', 'update_failed', 'deactivated'] and deploy_id:
            print(f"\n  📋 Logs for failed deploy {deploy['id']}:")
            logs_response = requests.get(
                f"https://api.render.com/v1/services/{SERVICE_ID}/deploys/{deploy['id']}/logs",
                headers=headers
            )
            if logs_response.status_code == 200:
                logs = logs_response.text
                print(logs[-2000:])  # Last 2000 chars
else:
    print(f"Error getting deploys: {deploys_response.status_code}")
    print(deploys_response.text)
