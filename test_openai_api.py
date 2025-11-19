"""
Test script to verify OpenAI API access with the new ROOK API key
Testing GPT-5, o3, o4-mini, and Responses API
"""

from openai import OpenAI
import os

# Set the API key
API_KEY = "YOUR_OPENAI_API_KEY"

# Initialize OpenAI client
client = OpenAI(api_key=API_KEY)

print("=" * 80)
print("Testing OpenAI API Access for ROOK")
print("=" * 80)

# Test 1: List available models
print("\n1. Listing available models...")
try:
    models = client.models.list()
    print("✅ Successfully connected to OpenAI API")
    print(f"Found {len(models.data)} models")
    
    # Look for GPT-5 and o-series models
    gpt5_models = [m for m in models.data if 'gpt-5' in m.id.lower()]
    o_models = [m for m in models.data if m.id.startswith('o')]
    
    print(f"\nGPT-5 models found: {len(gpt5_models)}")
    for model in gpt5_models[:5]:
        print(f"  - {model.id}")
    
    print(f"\no-series models found: {len(o_models)}")
    for model in o_models[:5]:
        print(f"  - {model.id}")
        
except Exception as e:
    print(f"❌ Error listing models: {e}")

# Test 2: Try using Responses API with gpt-5
print("\n" + "=" * 80)
print("2. Testing Responses API with gpt-5...")
print("=" * 80)
try:
    response = client.responses.create(
        model="gpt-5",
        input="Say 'Hello from ROOK' in exactly 5 words.",
        reasoning={"effort": "minimal"},
        text={"verbosity": "low"}
    )
    print("✅ Responses API works!")
    print(f"Response: {response.output_text}")
    print(f"Model used: {response.model}")
    
except Exception as e:
    print(f"❌ Error with Responses API: {e}")

# Test 3: Try embeddings (for personality/knowledge base)
print("\n" + "=" * 80)
print("3. Testing embeddings API...")
print("=" * 80)
try:
    embedding_response = client.embeddings.create(
        model="text-embedding-3-large",
        input="Test embedding for ROOK personality system",
        dimensions=3072
    )
    print("✅ Embeddings API works!")
    print(f"Embedding dimensions: {len(embedding_response.data[0].embedding)}")
    
except Exception as e:
    print(f"❌ Error with embeddings: {e}")

# Test 4: Try o3 model
print("\n" + "=" * 80)
print("4. Testing o3 reasoning model...")
print("=" * 80)
try:
    response = client.responses.create(
        model="o3",
        input="What is 2+2? Think step by step.",
        reasoning={"effort": "low"}
    )
    print("✅ o3 model works!")
    print(f"Response: {response.output_text}")
    
except Exception as e:
    print(f"❌ Error with o3: {e}")

# Test 5: Try o4-mini model
print("\n" + "=" * 80)
print("5. Testing o4-mini reasoning model...")
print("=" * 80)
try:
    response = client.responses.create(
        model="o4-mini",
        input="What is 2+2?",
        reasoning={"effort": "minimal"}
    )
    print("✅ o4-mini model works!")
    print(f"Response: {response.output_text}")
    
except Exception as e:
    print(f"❌ Error with o4-mini: {e}")

print("\n" + "=" * 80)
print("API Testing Complete!")
print("=" * 80)
