"""
Set environment variables in Render
"""

import requests
import sys

RENDER_API_KEY = "rnd_9gdSQ9VFF1ChnMU5qu9Op9k4JQKx"
SERVICE_ID = "srv-d4f03la4d50c73e4lt7g"

headers = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Content-Type": "application/json"
}

def set_env_var(key, value):
    """Set an environment variable"""
    data = {
        "key": key,
        "value": value
    }
    
    response = requests.put(
        f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars/{key}",
        headers=headers,
        json=data
    )
    
    if response.status_code in [200, 201]:
        print(f"✅ Set {key}")
        return True
    else:
        print(f"❌ Failed to set {key}: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python set_render_env.py KEY VALUE")
        print("\nExample:")
        print("  python set_render_env.py OPENAI_API_KEY sk-...")
        print("  python set_render_env.py PINECONE_API_KEY pcsk_...")
        print("  python set_render_env.py NEWSAPI_KEY ...")
        sys.exit(1)
    
    key = sys.argv[1]
    value = sys.argv[2]
    
    set_env_var(key, value)
