"""
Simple test of ROOK with foundational memory
"""

from openai import OpenAI
from pinecone import Pinecone

# Initialize clients
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"

client = OpenAI(api_key=OPENAI_API_KEY, base_url='https://api.openai.com/v1')
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("rook-memory")

def create_embedding(text):
    """Create embedding for text"""
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return response.data[0].embedding

def retrieve_memories(query, top_k=5):
    """Retrieve relevant memories from Pinecone"""
    query_embedding = create_embedding(query)
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    return results.matches

def test_rook(query):
    """Test ROOK with a query"""
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"{'='*80}\n")
    
    # Retrieve relevant memories
    memories = retrieve_memories(query, top_k=5)
    
    print(f"Retrieved {len(memories)} relevant memories:\n")
    for i, mem in enumerate(memories, 1):
        print(f"{i}. [{mem.id}] (score: {mem.score:.3f})")
        print(f"   {mem.metadata.get('content', '')[:150]}...\n")
    
    # Build context from memories
    memory_context = "\n\n".join([
        f"Memory: {mem.metadata.get('content', '')}"
        for mem in memories
    ])
    
    # Create system prompt
    system_prompt = f"""You are ROOK, an AI investigative journalist.

Your personality and knowledge emerge from your memories and experiences:

{memory_context}

Respond naturally based on these memories. Let your personality emerge from what you've learned and experienced."""
    
    # Generate response
    print("Generating ROOK's response...\n")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.7
    )
    
    print(f"ROOK's Response:\n")
    print(response.choices[0].message.content)
    print(f"\n{'='*80}\n")

# Run tests
print("\n" + "="*80)
print("TESTING ROOK WITH FOUNDATIONAL MEMORY")
print("="*80)

test_rook("Tell me about yourself.")

input("\nPress Enter to continue...")

test_rook("What do you think about the golden mole?")

input("\nPress Enter to continue...")

test_rook("I'm investigating a company that seems too complex to understand. What should I look for?")

input("\nPress Enter to continue...")

test_rook("Do you ever wish you could do field reporting?")

print("\n" + "="*80)
print("TESTING COMPLETE")
print("="*80)
print("\nROOK's personality emerged from his foundational memories.")
print("No hardcoded phrasing. Pure emergence.")
