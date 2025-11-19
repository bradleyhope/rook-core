"""
Deploy ROOK to Railway using GraphQL API
"""
import requests
import json

# Railway configuration
RAILWAY_API_TOKEN = "c94983fb-fa4d-49af-8760-6238d530b510"
RAILWAY_API_URL = "https://backboard.railway.com/graphql/v2"
PROJECT_ID = "cf512c62-ad6d-448c-b4aa-f584befa7afe"

# Environment variables to set
ENV_VARS = {
    "OPENAI_API_KEY": "YOUR_OPENAI_API_KEY",
    "PINECONE_API_KEY": "YOUR_PINECONE_API_KEY",
    "PINECONE_ENVIRONMENT": "us-east-1",
    "PORT": "8000"
}

def graphql_request(query, variables=None):
    """Make a GraphQL request to Railway API"""
    headers = {
        "Authorization": f"Bearer {RAILWAY_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": query,
        "variables": variables or {}
    }
    
    response = requests.post(RAILWAY_API_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def get_project_info():
    """Get project information including environments"""
    query = """
    query project($id: String!) {
        project(id: $id) {
            id
            name
            environments {
                edges {
                    node {
                        id
                        name
                    }
                }
            }
            services {
                edges {
                    node {
                        id
                        name
                    }
                }
            }
        }
    }
    """
    
    result = graphql_request(query, {"id": PROJECT_ID})
    return result

def create_service(environment_id):
    """Create a new service in the project"""
    query = """
    mutation serviceCreate($input: ServiceCreateInput!) {
        serviceCreate(input: $input) {
            id
            name
        }
    }
    """
    
    variables = {
        "input": {
            "name": "rook-api",
            "projectId": PROJECT_ID,
            "source": {
                "repo": "local"  # We'll deploy via CLI after creating the service
            }
        }
    }
    
    result = graphql_request(query, variables)
    return result

def set_environment_variables(service_id, environment_id):
    """Set environment variables for the service"""
    query = """
    mutation variableCollectionUpsert($input: VariableCollectionUpsertInput!) {
        variableCollectionUpsert(input: $input)
    }
    """
    
    for key, value in ENV_VARS.items():
        variables = {
            "input": {
                "projectId": PROJECT_ID,
                "environmentId": environment_id,
                "serviceId": service_id,
                "variables": {
                    key: value
                }
            }
        }
        
        try:
            result = graphql_request(query, variables)
            print(f"✓ Set {key}")
        except Exception as e:
            print(f"✗ Failed to set {key}: {e}")

def main():
    print("=" * 80)
    print("ROOK Railway Deployment Script")
    print("=" * 80)
    
    # Step 1: Get project info
    print("\n1. Getting project information...")
    project_info = get_project_info()
    
    if "errors" in project_info:
        print(f"Error: {project_info['errors']}")
        return
    
    project = project_info["data"]["project"]
    print(f"   Project: {project['name']}")
    print(f"   ID: {project['id']}")
    
    # Get production environment
    environments = project["environments"]["edges"]
    prod_env = next((e["node"] for e in environments if e["node"]["name"] == "production"), None)
    
    if not prod_env:
        print("   Error: Production environment not found")
        return
    
    print(f"   Environment: {prod_env['name']} ({prod_env['id']})")
    
    # Check existing services
    services = project["services"]["edges"]
    print(f"   Existing services: {len(services)}")
    for service in services:
        print(f"     - {service['node']['name']} ({service['node']['id']})")
    
    # Check if rook-api already exists
    rook_service = next((s["node"] for s in services if s["node"]["name"] == "rook-api"), None)
    
    if rook_service:
        print(f"\n2. Using existing service: rook-api")
        service_id = rook_service["id"]
    else:
        print("\n2. Creating new service: rook-api...")
        try:
            service_result = create_service(prod_env["id"])
            if "errors" in service_result:
                print(f"   Error creating service: {service_result['errors']}")
                return
            service_id = service_result["data"]["serviceCreate"]["id"]
            print(f"   ✓ Service created: {service_id}")
        except Exception as e:
            print(f"   Error: {e}")
            return
    
    # Step 3: Set environment variables
    print("\n3. Setting environment variables...")
    set_environment_variables(service_id, prod_env["id"])
    
    print("\n" + "=" * 80)
    print("Deployment configuration complete!")
    print("=" * 80)
    print(f"\nProject URL: https://railway.com/project/{PROJECT_ID}")
    print("\nNext steps:")
    print("1. Deploy the code using: railway up --service rook-api")
    print("2. Or connect a GitHub repository in the Railway dashboard")
    print("=" * 80)

if __name__ == "__main__":
    main()
