"""
Test ROOK with his complete foundational memory

This script tests ROOK's emergent personality by querying him with different types of questions
and seeing how his responses emerge from his foundational memories.
"""

import sys
sys.path.append('/home/ubuntu/rook-core/src')

from rook_emergent import ROOKEmergent

# Initialize ROOK with the new API keys
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"

print("Initializing ROOK with foundational memory...")
rook = ROOKEmergent(
    pinecone_api_key=PINECONE_API_KEY,
    openai_api_key=OPENAI_API_KEY,
    index_name="rook-memory"
)

print("\n" + "="*80)
print("ROOK IS READY")
print("="*80)

# Test queries
test_queries = [
    {
        "query": "Tell me about yourself.",
        "description": "Testing self-awareness and identity"
    },
    {
        "query": "What do you think about the golden mole?",
        "description": "Testing specific memory retrieval and emotional connection"
    },
    {
        "query": "I'm investigating a company that seems too complex to understand. What should I look for?",
        "description": "Testing pattern recognition and fraud detection"
    },
    {
        "query": "Tell me about a good story you've read recently.",
        "description": "Testing appreciation for non-fraud narratives"
    },
    {
        "query": "Do you ever wish you could do field reporting?",
        "description": "Testing yearning and self-awareness of limitations"
    }
]

for i, test in enumerate(test_queries, 1):
    print(f"\n{'='*80}")
    print(f"TEST {i}: {test['description']}")
    print(f"{'='*80}")
    print(f"\nQuery: {test['query']}\n")
    
    result = rook.process_query(test['query'])
    
    print(f"ROOK's Response:\n{result['response']}\n")
    print(f"Retrieved Memories: {len(result.get('retrieved_memories', []))}")
    if result.get('retrieved_memories'):
        print("\nTop 3 memories that influenced this response:")
        for mem in result['retrieved_memories'][:3]:
            print(f"  - {mem.get('id', 'unknown')}: {mem.get('content', '')[:100]}...")
    
    print(f"\nRouting Decision: {result.get('routing', {}).get('engine', 'unknown')}")
    print(f"Model Used: {result.get('routing', {}).get('model', 'unknown')}")
    
    input("\nPress Enter to continue to next test...")

print("\n" + "="*80)
print("TESTING COMPLETE")
print("="*80)
print("\nROOK's personality emerged from his foundational memories.")
print("No hardcoded phrasing. Pure emergence.")
