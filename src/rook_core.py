"""
ROOK Core System

Main integration point that brings together:
- Personality & Memory Layer
- Query & Routing Engine  
- Task Execution Engine
- Knowledge Base Access
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from personality.personality_layer import PersonalityLayer
from routing.routing_engine import RoutingEngine
from openai import OpenAI
from typing import Dict, List

class ROOKCore:
    """
    Main ROOK system that coordinates all components.
    """
    
    def __init__(self, pinecone_api_key: str, openai_api_key: str):
        """
        Initialize ROOK Core System.
        
        Args:
            pinecone_api_key: Pinecone API key
            openai_api_key: OpenAI API key
        """
        print("🤖 Initializing ROOK Core System...")
        
        # Initialize components
        self.personality = PersonalityLayer(
            pinecone_api_key=pinecone_api_key,
            openai_api_key=openai_api_key
        )
        print("✅ Personality Layer initialized")
        
        self.router = RoutingEngine(openai_api_key=openai_api_key)
        print("✅ Routing Engine initialized")
        
        self.openai_client = OpenAI(
            api_key=openai_api_key,
            base_url='https://api.openai.com/v1'
        )
        print("✅ OpenAI Client initialized")
        
        print("🎉 ROOK Core System ready!\n")
    
    def process_query(self, query: str, user_id: str = "default", stream: bool = False) -> Dict:
        """
        Process a user query through the complete ROOK pipeline.
        
        Args:
            query: The user's query
            user_id: Unique identifier for the user
            stream: Whether to stream the response
            
        Returns:
            Dictionary containing the response and metadata
        """
        print(f"📝 Processing query: {query}\n")
        
        # Step 1: Enrich query with personality and memory
        print("🧠 Step 1: Enriching query with ROOK's personality...")
        enriched = self.personality.enrich_query(query, user_id)
        system_prompt = enriched["system_prompt"]
        conversation_history = enriched["conversation_history"]
        
        # Step 2: Route the query
        print("🔀 Step 2: Analyzing and routing query...")
        routing = self.router.route_query(query, system_prompt)
        print(f"   Query Type: {routing['analysis'].get('query_type', 'N/A')}")
        print(f"   Execution Engine: {routing['routing_decision']['execution_engine']}")
        print(f"   Model: {routing['routing_decision']['model']}")
        print(f"   Tools: {routing['routing_decision']['tools']}\n")
        
        # Step 3: Execute the query
        print("⚙️  Step 3: Executing query...")
        response = self._execute_query(
            query=query,
            system_prompt=system_prompt,
            conversation_history=conversation_history,
            routing_decision=routing['routing_decision'],
            stream=stream
        )
        
        # Step 4: Update conversation history
        self.personality.add_to_conversation_history(user_id, "user", query)
        self.personality.add_to_conversation_history(user_id, "assistant", response['content'])
        
        return {
            "query": query,
            "response": response['content'],
            "routing": routing,
            "model_used": response['model'],
            "tokens_used": response.get('tokens', {})
        }
    
    def _execute_query(
        self, 
        query: str, 
        system_prompt: str,
        conversation_history: List[Dict],
        routing_decision: Dict,
        stream: bool = False
    ) -> Dict:
        """
        Execute a query using the appropriate model and tools.
        
        Args:
            query: The user's query
            system_prompt: ROOK's personality-enriched system prompt
            conversation_history: Previous conversation messages
            routing_decision: Routing information from the router
            stream: Whether to stream the response
            
        Returns:
            Dictionary containing the response
        """
        model = routing_decision['model']
        execution_engine = routing_decision['execution_engine']
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": query})
        
        # Execute based on routing decision
        if execution_engine == "deep_research":
            return self._execute_deep_research(messages, model)
        elif execution_engine == "reasoning_engine":
            return self._execute_reasoning(messages, model)
        elif execution_engine == "web_research_engine":
            return self._execute_web_research(messages, model)
        else:  # chat_engine
            return self._execute_chat(messages, model)
    
    def _execute_chat(self, messages: List[Dict], model: str) -> Dict:
        """Execute a simple chat completion."""
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=messages
        )
        
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "tokens": {
                "prompt": response.usage.prompt_tokens,
                "completion": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }
        }
    
    def _execute_reasoning(self, messages: List[Dict], model: str) -> Dict:
        """Execute with reasoning models (o3, o4-mini)."""
        # For now, use chat completions
        # TODO: Implement Responses API when available
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=messages
        )
        
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "tokens": {
                "prompt": response.usage.prompt_tokens,
                "completion": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }
        }
    
    def _execute_web_research(self, messages: List[Dict], model: str) -> Dict:
        """Execute with web search capabilities."""
        # For now, use standard chat
        # TODO: Implement web search tool integration
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=messages
        )
        
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "tokens": {
                "prompt": response.usage.prompt_tokens,
                "completion": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }
        }
    
    def _execute_deep_research(self, messages: List[Dict], model: str) -> Dict:
        """Execute deep research investigation."""
        # For now, use reasoning model
        # TODO: Implement Deep Research API when available
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=messages
        )
        
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "tokens": {
                "prompt": response.usage.prompt_tokens,
                "completion": response.usage.completion_tokens,
                "total": response.usage.total_tokens
            }
        }


# Example usage
if __name__ == "__main__":
    # API keys
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY', 'YOUR_PINECONE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY')
    
    # Initialize ROOK
    rook = ROOKCore(
        pinecone_api_key=PINECONE_API_KEY,
        openai_api_key=OPENAI_API_KEY
    )
    
    # Test query
    print("=" * 80)
    print("ROOK CORE SYSTEM TEST")
    print("=" * 80 + "\n")
    
    test_query = "I'm investigating a series of shell companies that appear to be layering funds. What documents should I request?"
    
    result = rook.process_query(test_query)
    
    print("\n" + "=" * 80)
    print("ROOK'S RESPONSE:")
    print("=" * 80)
    print(result['response'])
    print("\n" + "=" * 80)
    print(f"Model Used: {result['model_used']}")
    print(f"Tokens: {result['tokens_used']['total']}")
    print("=" * 80)
