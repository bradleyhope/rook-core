#!/usr/bin/env python3
"""
View ROOK's Memories from Pinecone

Shows all formative memories and experiences stored in the rook-memory index.
"""

from pinecone import Pinecone
from openai import OpenAI
import json

PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

def main():
    print("=" * 80)
    print("🧠 ROOK's Memories from Pinecone")
    print("=" * 80)
    print()
    
    # Initialize Pinecone
    print("Connecting to Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Connect to rook-memory index
    index = pc.Index("rook-memory")
    
    # Get stats
    stats = index.describe_index_stats()
    print(f"Total memories: {stats.total_vector_count}\n")
    
    # Create a query vector (we'll use a dummy vector to fetch all)
    # We need to create an embedding to query
    openai_client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url='https://api.openai.com/v1'
    )
    
    # Create embedding for a general query
    query_text = "formative experiences and memories"
    embedding_response = openai_client.embeddings.create(
        model="text-embedding-3-large",
        input=query_text,
        dimensions=3072
    )
    query_vector = embedding_response.data[0].embedding
    
    # Query to get all memories
    print("Retrieving all memories...\n")
    results = index.query(
        vector=query_vector,
        top_k=100,  # Get up to 100 memories
        include_metadata=True
    )
    
    print("=" * 80)
    print(f"Found {len(results.matches)} memories")
    print("=" * 80)
    print()
    
    # Display each memory
    for i, match in enumerate(results.matches, 1):
        metadata = match.metadata
        
        print(f"\n{'=' * 80}")
        print(f"Memory #{i}: {match.id}")
        print(f"Score: {match.score:.4f}")
        print(f"{'=' * 80}")
        
        # Display metadata
        if 'memory_type' in metadata:
            print(f"Type: {metadata['memory_type']}")
        
        if 'content' in metadata:
            print(f"\nContent:\n{metadata['content']}")
        
        if 'importance' in metadata:
            print(f"\nImportance: {metadata['importance']}/10")
        
        if 'emotional_valence' in metadata:
            valence = metadata['emotional_valence']
            emotion = "Positive" if valence > 0 else "Negative" if valence < 0 else "Neutral"
            print(f"Emotional Valence: {valence} ({emotion})")
        
        if 'personality_impact' in metadata:
            print(f"\nPersonality Impact:\n{metadata['personality_impact']}")
        
        if 'consolidation_state' in metadata:
            print(f"\nConsolidation State: {metadata['consolidation_state']}")
        
        if 'access_count' in metadata:
            print(f"Access Count: {metadata['access_count']}")
        
        if 'timestamp' in metadata:
            print(f"Timestamp: {metadata['timestamp']}")
        
        if 'tags' in metadata:
            print(f"Tags: {metadata['tags']}")
        
        print()
    
    print("\n" + "=" * 80)
    print("✅ Memory retrieval complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
