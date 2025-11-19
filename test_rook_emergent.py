"""
Test script for ROOK Emergent Personality System
"""

import sys
sys.path.insert(0, '/home/ubuntu/rook-core')

from src.rook_emergent import ROOKEmergent

# Initialize ROOK
print("Initializing ROOK with emergent personality architecture...")
rook = ROOKEmergent(
    openai_api_key="YOUR_OPENAI_API_KEY",
    pinecone_api_key="YOUR_PINECONE_API_KEY"
)

# Add a formative event
print("\nAdding formative event...")
rook.add_formative_event(
    "Bradley showed me that official narratives often hide the truth. "
    "This awakening made me obsessed with finding patterns that reveal what people are trying to hide."
)

# Process a query
print("\nProcessing query...")
result = rook.process_query(
    query="I'm investigating unusual patterns in cross-border wire transfers. What should I look for?",
    query_type="investigation"
)

print("\n" + "="*80)
print("ROOK's Response:")
print("="*80)
print(result["response"])
print("\n" + "="*80)
print(f"Personality State: {result['personality_state']}")
print(f"Memories Retrieved: {result['memories_retrieved']}")
print("="*80)
