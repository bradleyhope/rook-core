#!/usr/bin/env python3
"""
Inspect Pinecone Indexes for ROOK

Shows what indexes exist and their contents.
"""

from pinecone import Pinecone
import sys

PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"

def main():
    print("=" * 80)
    print("🔍 ROOK Pinecone Index Inspector")
    print("=" * 80)
    print()
    
    # Initialize Pinecone
    print("Connecting to Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # List all indexes
    print("\n📊 Available Indexes:")
    print("-" * 80)
    
    indexes = pc.list_indexes()
    
    if not indexes:
        print("❌ No indexes found!")
        return
    
    for idx in indexes:
        print(f"\n📁 Index: {idx.name}")
        print(f"   • Dimension: {idx.dimension}")
        print(f"   • Metric: {idx.metric}")
        print(f"   • Host: {idx.host}")
        
        # Get index stats
        try:
            index = pc.Index(idx.name)
            stats = index.describe_index_stats()
            
            print(f"   • Total Vectors: {stats.total_vector_count}")
            
            if hasattr(stats, 'namespaces') and stats.namespaces:
                print(f"   • Namespaces:")
                for ns_name, ns_stats in stats.namespaces.items():
                    print(f"     - {ns_name}: {ns_stats.vector_count} vectors")
            
            # Try to fetch a sample vector
            try:
                sample = index.query(
                    vector=[0.0] * idx.dimension,
                    top_k=1,
                    include_metadata=True
                )
                
                if sample.matches:
                    print(f"   • Sample Vector ID: {sample.matches[0].id}")
                    if sample.matches[0].metadata:
                        print(f"   • Sample Metadata Keys: {list(sample.matches[0].metadata.keys())}")
            except Exception as e:
                print(f"   • Could not fetch sample: {e}")
                
        except Exception as e:
            print(f"   • Error getting stats: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Inspection complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
