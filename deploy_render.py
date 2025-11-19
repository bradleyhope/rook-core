#!/usr/bin/env python3
"""
Deploy ROOK to Render.com via API
"""
import requests
import json
import sys

RENDER_API_KEY = "rnd_9gdSQ9VFF1ChnMU5qu9Op9k4JQKx"
BASE_URL = "https://api.render.com/v1"

headers = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "accept": "application/json",
    "content-type": "application/json"
}

def get_owner_id():
    """Get the workspace/owner ID"""
    print("📋 Getting workspace ID...")
    response = requests.get(f"{BASE_URL}/owners", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Error getting workspaces: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    data = response.json()
    if not data or len(data) == 0:
        print("❌ No workspaces found")
        sys.exit(1)
    
    owner = data[0]["owner"]
    owner_id = owner["id"]
    owner_name = owner.get("name", owner.get("email", "Unknown"))
    
    print(f"✅ Found workspace: {owner_name}")
    print(f"   Owner ID: {owner_id}")
    return owner_id

def create_service(owner_id):
    """Create the ROOK web service"""
    print("\n🚀 Creating ROOK web service...")
    
    # Note: Render API requires a GitHub repo for web services
    # We'll need to push the code to GitHub first
    service_data = {
        "type": "web_service",
        "name": "rook-chat",
        "ownerId": owner_id,
        "repo": "https://github.com/YOUR_USERNAME/rook-core",  # Need to update this
        "autoDeploy": "yes",
        "serviceDetails": {
            "env": "python",
            "plan": "starter",  # $7/month minimum for API
            "region": "oregon",
            "buildCommand": "pip install --upgrade pip && pip install -r requirements.txt",
            "startCommand": "cd api && uvicorn chat_server:app --host 0.0.0.0 --port $PORT",
            "envVars": [
                {"key": "PYTHON_VERSION", "value": "3.11.0"},
                {"key": "OPENAI_API_KEY", "value": ""},  # Set via dashboard
                {"key": "PINECONE_API_KEY", "value": "YOUR_PINECONE_API_KEY"},
                {"key": "PINECONE_ENVIRONMENT", "value": "us-east-1"}
            ]
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/services",
        headers=headers,
        json=service_data
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ Error creating service: {response.status_code}")
        print(response.text)
        return None
    
    service = response.json()
    service_id = service.get("service", {}).get("id")
    service_url = service.get("service", {}).get("serviceDetails", {}).get("url")
    
    print(f"✅ Service created!")
    print(f"   Service ID: {service_id}")
    print(f"   URL: {service_url}")
    
    return service_id

def main():
    print("=" * 60)
    print("ROOK Render Deployment")
    print("=" * 60)
    
    # Step 1: Get workspace ID
    owner_id = get_owner_id()
    
    # Step 2: Create service
    print("\n⚠️  IMPORTANT: Render API requires a GitHub repository")
    print("   You need to:")
    print("   1. Push ROOK code to GitHub")
    print("   2. Update the 'repo' URL in this script")
    print("   3. Run this script again")
    print("\n   OR deploy manually via Render Dashboard")
    print("   See RENDER_DEPLOYMENT.md for instructions")
    
    # Uncomment when GitHub repo is ready:
    # service_id = create_service(owner_id)
    
    print("\n" + "=" * 60)
    print("Workspace ID for manual deployment:", owner_id)
    print("=" * 60)

if __name__ == "__main__":
    main()
