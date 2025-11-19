"""
ROOK Personality & Memory Layer

This module is responsible for injecting ROOK's unique personality and memory
into every interaction. It retrieves personality vectors from Pinecone and
conversation history from the database to create a rich, context-aware system prompt.
"""

import os
from typing import Dict, List, Optional
from pinecone import Pinecone
from openai import OpenAI

class PersonalityLayer:
    """
    Manages ROOK's personality and memory system.
    """
    
    def __init__(self, pinecone_api_key: str, openai_api_key: str, personality_index_name: str = "rook-personality-and-knowledge"):
        """
        Initialize the Personality Layer with Pinecone and OpenAI clients.
        
        Args:
            pinecone_api_key: Pinecone API key
            openai_api_key: OpenAI API key
            personality_index_name: Name of the Pinecone index containing personality data
        """
        self.pinecone_client = Pinecone(api_key=pinecone_api_key)
        # Use direct OpenAI API (bypass Manus proxy)
        self.openai_client = OpenAI(
            api_key=openai_api_key,
            base_url='https://api.openai.com/v1'
        )
        
        # Connect to personality index
        self.personality_index = self.pinecone_client.Index(personality_index_name)
        
        # In-memory conversation history (will be replaced with database in Phase 2)
        self.conversation_history: Dict[str, List[Dict]] = {}
        
    def get_personality_context(self, query: str, top_k: int = 5) -> str:
        """
        Retrieve relevant personality vectors based on the query.
        
        Args:
            query: The user's query
            top_k: Number of personality vectors to retrieve
            
        Returns:
            A formatted string containing relevant personality context
        """
        # Generate embedding for the query
        embedding_response = self.openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=query,
            dimensions=3072
        )
        query_embedding = embedding_response.data[0].embedding
        
        # Query Pinecone for relevant personality vectors
        results = self.personality_index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Format personality context - purely from vectors, no hardcoded text
        personality_parts = []
        for match in results.matches:
            if match.score > 0.7:  # Only include high-confidence matches
                text = match.metadata.get('text', '')
                if text:
                    personality_parts.append(text)
        
        return "\n\n".join(personality_parts) if personality_parts else ""
    
    def get_conversation_history(self, user_id: str, max_turns: int = 5) -> List[Dict]:
        """
        Retrieve recent conversation history for a user.
        
        Args:
            user_id: Unique identifier for the user
            max_turns: Maximum number of conversation turns to retrieve
            
        Returns:
            List of conversation messages
        """
        if user_id not in self.conversation_history:
            return []
        
        # Return the most recent turns
        return self.conversation_history[user_id][-max_turns*2:]  # *2 for user+assistant pairs
    
    def add_to_conversation_history(self, user_id: str, role: str, content: str):
        """
        Add a message to the conversation history.
        
        Args:
            user_id: Unique identifier for the user
            role: 'user' or 'assistant'
            content: The message content
        """
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "role": role,
            "content": content
        })
    
    def build_system_prompt(self, query: str, user_id: str = "default") -> str:
        """
        Build a complete system prompt that includes ROOK's personality and memory.
        
        Args:
            query: The user's current query
            user_id: Unique identifier for the user
            
        Returns:
            A comprehensive system prompt for the AI model
        """
        # Get relevant personality context from Pinecone
        # This is the ONLY source of ROOK's identity - no hardcoded phrasing
        personality_context = self.get_personality_context(query)
        
        # The full prompt is purely from the personality vectors
        full_prompt = personality_context
        
        return full_prompt
    
    def enrich_query(self, query: str, user_id: str = "default") -> Dict:
        """
        Enrich a user query with personality and memory context.
        
        Args:
            query: The user's query
            user_id: Unique identifier for the user
            
        Returns:
            A dictionary containing the system prompt and conversation history
        """
        system_prompt = self.build_system_prompt(query, user_id)
        conversation_history = self.get_conversation_history(user_id)
        
        return {
            "system_prompt": system_prompt,
            "conversation_history": conversation_history,
            "user_query": query
        }


# Example usage
if __name__ == "__main__":
    import sys
    
    # Get API keys from command line or environment
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY', 'YOUR_PINECONE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY')
    
    # Initialize the personality layer
    print("Initializing ROOK Personality Layer...")
    personality = PersonalityLayer(
        pinecone_api_key=PINECONE_API_KEY,
        openai_api_key=OPENAI_API_KEY
    )
    
    # Test query
    test_query = "I'm analyzing a network of offshore accounts with unusual transaction patterns. What should I investigate first?"
    
    print(f"\nTest Query: {test_query}\n")
    print("=" * 80)
    
    # Enrich the query
    enriched = personality.enrich_query(test_query)
    
    print("SYSTEM PROMPT:")
    print("=" * 80)
    print(enriched["system_prompt"])
    print("\n" + "=" * 80)
    print("USER QUERY:")
    print("=" * 80)
    print(enriched["user_query"])
    
    print("\n✅ Personality Layer test complete!")
