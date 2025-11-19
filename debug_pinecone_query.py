#!/usr/bin/env python3
"""Debug Pinecone queries in detail"""

from pinecone import Pinecone
from openai import OpenAI

PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

print("=" * 80)
print("Detailed Pinecone Query Debug")
print("=" * 80)
print()

# Initialize
print("Initializing Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)
print("✅ Pinecone initialized\n")

print("Initializing OpenAI...")
openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url='https://api.openai.com/v1'
)
print("✅ OpenAI initialized\n")

# Connect to personality index
print("Connecting to rook-personality-and-knowledge index...")
personality_index = pc.Index("rook-personality-and-knowledge")
print("✅ Connected\n")

# Get index stats
print("Getting index stats...")
stats = personality_index.describe_index_stats()
print(f"Total vectors: {stats.total_vector_count}")
print(f"Dimension: {stats.dimension if hasattr(stats, 'dimension') else 'N/A'}")
print()

# Create embedding
test_query = "tell me about yourself"
print(f"Test query: '{test_query}'")
print("Creating embedding...")

embedding_response = openai_client.embeddings.create(
    model="text-embedding-3-large",
    input=test_query,
    dimensions=3072
)
query_embedding = embedding_response.data[0].embedding

print(f"✅ Embedding created (dimension: {len(query_embedding)})\n")

# Query Pinecone
print("Querying Pinecone...")
results = personality_index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True
)

print(f"Results returned: {len(results.matches)}\n")

# Show all results
print("=" * 80)
print("All Results:")
print("=" * 80)

for i, match in enumerate(results.matches, 1):
    print(f"\nMatch #{i}:")
    print(f"  ID: {match.id}")
    print(f"  Score: {match.score:.4f}")
    print(f"  Metadata keys: {list(match.metadata.keys())}")
    
    if 'text' in match.metadata:
        text = match.metadata['text']
        print(f"  Text length: {len(text)} chars")
        print(f"  Text preview: {text[:200]}...")
    
    if 'category' in match.metadata:
        print(f"  Category: {match.metadata['category']}")
    
    if 'section' in match.metadata:
        print(f"  Section: {match.metadata['section']}")

print("\n" + "=" * 80)
print("✅ Debug complete!")
print("=" * 80)
