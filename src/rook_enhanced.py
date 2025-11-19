"""
ROOK Enhanced Core System

Fully integrated system with:
- Personality & Memory Layer
- Query & Routing Engine
- Knowledge Base Access
- Task Execution with o3/o4-mini/gpt-5
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from personality.personality_layer import PersonalityLayer
from routing.routing_engine import RoutingEngine
from knowledge.knowledge_base import KnowledgeBase
from openai import OpenAI
from typing import Dict, List

class ROOKEnhanced:
    """
    Enhanced ROOK system with full knowledge base integration.
    """
    
    def __init__(self, pinecone_api_key: str, openai_api_key: str):
        """
        Initialize Enhanced ROOK Core System.
        
        Args:
            pinecone_api_key: Pinecone API key
            openai_api_key: OpenAI API key
        """
        print("🤖 Initializing ROOK Enhanced Core System...")
        print("=" * 80 + "\n")
        
        # Initialize components
        self.personality = PersonalityLayer(
            pinecone_api_key=pinecone_api_key,
            openai_api_key=openai_api_key
        )
        print("✅ Personality Layer initialized")
        
        self.router = RoutingEngine(openai_api_key=openai_api_key)
        print("✅ Routing Engine initialized")
        
        self.knowledge_base = KnowledgeBase(
            pinecone_api_key=pinecone_api_key,
            openai_api_key=openai_api_key
        )
        print(f"✅ Knowledge Base initialized ({len(self.knowledge_base.indexes)} indexes)")
        
        self.openai_client = OpenAI(
            api_key=openai_api_key,
            base_url='https://api.openai.com/v1'
        )
        print("✅ OpenAI Client initialized")
        
        print("\n" + "=" * 80)
        print("🎉 ROOK Enhanced System Ready!")
        print("=" * 80 + "\n")
    
    def process_query(self, query: str, user_id: str = "default", verbose: bool = True) -> Dict:
        """
        Process a user query through the complete ROOK pipeline.
        
        Args:
            query: The user's query
            user_id: Unique identifier for the user
            verbose: Whether to print progress information
            
        Returns:
            Dictionary containing the response and metadata
        """
        if verbose:
            print(f"📝 Query: {query}\n")
            print("=" * 80)
        
        # Step 1: Enrich query with personality and memory
        if verbose:
            print("🧠 Step 1: Enriching with ROOK's personality...")
        enriched = self.personality.enrich_query(query, user_id)
        system_prompt = enriched["system_prompt"]
        conversation_history = enriched["conversation_history"]
        
        # Step 2: Route the query
        if verbose:
            print("🔀 Step 2: Analyzing and routing query...")
        routing = self.router.route_query(query, system_prompt)
        query_type = routing['analysis'].get('query_type') or routing['analysis'].get('Query Type', 'simple_chat')
        
        if verbose:
            print(f"   • Query Type: {query_type}")
            print(f"   • Execution Engine: {routing['routing_decision']['execution_engine']}")
            print(f"   • Model: {routing['routing_decision']['model']}")
        
        # Step 3: Retrieve relevant knowledge
        if verbose:
            print("📚 Step 3: Searching knowledge base...")
        kb_context = self.knowledge_base.get_context_for_query(query, query_type)
        if kb_context and verbose:
            print(f"   • Found relevant context ({len(kb_context)} chars)")
        
        # Step 4: Execute the query
        if verbose:
            print("⚙️  Step 4: Executing query...")
        response = self._execute_query(
            query=query,
            system_prompt=system_prompt,
            kb_context=kb_context,
            conversation_history=conversation_history,
            routing_decision=routing['routing_decision']
        )
        
        # Step 5: Update conversation history
        self.personality.add_to_conversation_history(user_id, "user", query)
        self.personality.add_to_conversation_history(user_id, "assistant", response['content'])
        
        if verbose:
            print("✅ Query processed successfully!")
            print("=" * 80 + "\n")
        
        return {
            "query": query,
            "response": response['content'],
            "routing": routing,
            "model_used": response['model'],
            "tokens_used": response.get('tokens', {}),
            "kb_context_used": bool(kb_context)
        }
    
    def _execute_query(
        self, 
        query: str, 
        system_prompt: str,
        kb_context: str,
        conversation_history: List[Dict],
        routing_decision: Dict
    ) -> Dict:
        """
        Execute a query using the appropriate model and tools.
        
        Args:
            query: The user's query
            system_prompt: ROOK's personality-enriched system prompt
            kb_context: Context from knowledge base
            conversation_history: Previous conversation messages
            routing_decision: Routing information from the router
            
        Returns:
            Dictionary containing the response
        """
        model = routing_decision['model']
        
        # Build enhanced system prompt with KB context (no hardcoded labels)
        if kb_context:
            enhanced_prompt = f"{system_prompt}\n\n{kb_context}"
        else:
            enhanced_prompt = system_prompt
        
        # Build messages
        messages = [{"role": "system", "content": enhanced_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": query})
        
        # Execute with appropriate model
        # Note: Some models (gpt-5, o-series) only support default temperature
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7
            )
        except Exception as e:
            if "temperature" in str(e):
                # Retry without temperature parameter
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages
                )
            else:
                raise
        
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "tokens": {
                "prompt": response.usage.prompt_tokens,
                "completion": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }
        }


# Example usage and interactive mode
if __name__ == "__main__":
    # API keys
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY', 'YOUR_PINECONE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY')
    
    # Initialize ROOK
    rook = ROOKEnhanced(
        pinecone_api_key=PINECONE_API_KEY,
        openai_api_key=OPENAI_API_KEY
    )
    
    # Test queries
    test_queries = [
        "Tell me about yourself.",
        "I'm investigating unusual patterns in cross-border wire transfers. What investigative steps should I take?",
        "What do you know about financial fraud in Southeast Asia?"
    ]
    
    print("\n" + "=" * 80)
    print("RUNNING TEST QUERIES")
    print("=" * 80 + "\n")
    
    for i, test_query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST QUERY {i}/{len(test_queries)}")
        print(f"{'='*80}\n")
        
        result = rook.process_query(test_query, verbose=True)
        
        print("💬 ROOK'S RESPONSE:")
        print("-" * 80)
        print(result['response'])
        print("\n" + "-" * 80)
        print(f"📊 Model: {result['model_used']}")
        print(f"📊 Tokens: {result['tokens_used']['total']}")
        print(f"📊 KB Context Used: {result['kb_context_used']}")
        print("=" * 80 + "\n")
        
        # Pause between queries
        if i < len(test_queries):
            input("Press Enter to continue to next query...")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETE!")
    print("=" * 80)
