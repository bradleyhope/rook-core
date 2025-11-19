#!/usr/bin/env python3
"""Debug ROOK personality retrieval"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from personality.personality_layer_with_storage import PersonalityLayerWithStorage

PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

print("=" * 80)
print("Testing ROOK Personality Retrieval")
print("=" * 80)
print()

print("Initializing personality layer...")
personality = PersonalityLayerWithStorage(
    pinecone_api_key=PINECONE_API_KEY,
    openai_api_key=OPENAI_API_KEY
)
print("✅ Initialized\n")

test_query = "tell me about yourself"

print(f"Test Query: {test_query}\n")
print("=" * 80)

# Get personality context
print("Getting personality context...")
personality_context = personality.get_personality_context(test_query, top_k=5)

print(f"\nPersonality Context Length: {len(personality_context)} chars")
print("=" * 80)
print("Personality Context:")
print("=" * 80)
print(personality_context)
print("=" * 80)
print()

# Get relevant memories
print("Getting relevant memories...")
memory_context = personality.get_relevant_memories(test_query, top_k=3)

print(f"\nMemory Context Length: {len(memory_context)} chars")
print("=" * 80)
print("Memory Context:")
print("=" * 80)
print(memory_context)
print("=" * 80)
print()

# Build full system prompt
print("Building system prompt...")
enriched = personality.enrich_query(test_query, "debug_user")
system_prompt = enriched["system_prompt"]

print(f"\nSystem Prompt Length: {len(system_prompt)} chars")
print("=" * 80)
print("System Prompt:")
print("=" * 80)
print(system_prompt)
print("=" * 80)
