#!/usr/bin/env python3
"""
Test ROOK Chat - Non-interactive Demo

Shows how ROOK responds to queries with memory and learning.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from personality.personality_layer_with_storage import PersonalityLayerWithStorage
from routing.routing_engine import RoutingEngine
from knowledge.knowledge_base import KnowledgeBase
from openai import OpenAI

PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

def test_rook():
    """Test ROOK with sample queries"""
    
    print("=" * 80)
    print("🔍 Testing ROOK Chat System")
    print("=" * 80)
    print()
    
    # Initialize
    print("Initializing ROOK...")
    personality = PersonalityLayerWithStorage(
        pinecone_api_key=PINECONE_API_KEY,
        openai_api_key=OPENAI_API_KEY
    )
    
    openai_client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url='https://api.openai.com/v1'
    )
    
    print("✅ ROOK initialized!\n")
    
    # Test queries
    test_queries = [
        "Hello ROOK! Who are you and what do you do?",
        "What fraud patterns should I look for in shell companies?",
        "Tell me about one of your formative experiences"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print("=" * 80)
        print(f"Query #{i}: {query}")
        print("=" * 80)
        print()
        
        # Enrich with personality and memories
        enriched = personality.enrich_query(query, "test_user")
        
        # Build messages
        messages = [
            {"role": "system", "content": enriched["system_prompt"]},
            {"role": "user", "content": query}
        ]
        
        # Get response
        print("🤔 ROOK is thinking...")
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        
        print(f"\n🔍 ROOK: {answer}\n")
        
        # Update conversation history
        personality.add_to_conversation_history("test_user", "user", query)
        personality.add_to_conversation_history("test_user", "assistant", answer)
        
        # Check if should store memory
        memory_analysis = personality.analyze_conversation_for_memory(query, answer)
        if memory_analysis:
            print("💾 This conversation is worth remembering!")
            print(f"   Reason: {memory_analysis['reason']}")
            print(f"   Importance: {memory_analysis['importance']}/10\n")
        
        print()
    
    print("=" * 80)
    print("✅ Test complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_rook()
