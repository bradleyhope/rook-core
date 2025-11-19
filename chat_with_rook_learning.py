#!/usr/bin/env python3
"""
ROOK Terminal Chat with Learning

ROOK can now create and store new memories from conversations!
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from personality.personality_layer_with_storage import PersonalityLayerWithStorage
from routing.routing_engine import RoutingEngine
from knowledge.knowledge_base import KnowledgeBase
from openai import OpenAI
from typing import Dict
import readline

# API Keys
PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

class ROOKWithLearning:
    """ROOK system with memory storage capabilities"""
    
    def __init__(self, pinecone_api_key: str, openai_api_key: str):
        """Initialize ROOK with learning"""
        print("🤖 Initializing ROOK with Learning Capabilities...")
        print("=" * 80 + "\n")
        
        self.personality = PersonalityLayerWithStorage(
            pinecone_api_key=pinecone_api_key,
            openai_api_key=openai_api_key
        )
        print("✅ Personality Layer with Storage initialized")
        
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
        print("🎉 ROOK with Learning Ready!")
        print("=" * 80 + "\n")
    
    def process_query(self, query: str, user_id: str = "default") -> Dict:
        """Process query and potentially store new memories"""
        
        # Enrich with personality and memories
        enriched = self.personality.enrich_query(query, user_id)
        system_prompt = enriched["system_prompt"]
        conversation_history = enriched["conversation_history"]
        
        # Route the query
        routing = self.router.route_query(query, system_prompt)
        query_type = routing['analysis'].get('query_type', 'simple_chat')
        
        # Get knowledge base context
        kb_context = self.knowledge_base.get_context_for_query(query, query_type)
        
        # Execute query
        response = self._execute_query(
            query=query,
            system_prompt=system_prompt,
            kb_context=kb_context,
            conversation_history=conversation_history,
            routing_decision=routing['routing_decision']
        )
        
        # Update conversation history
        self.personality.add_to_conversation_history(user_id, "user", query)
        self.personality.add_to_conversation_history(user_id, "assistant", response['content'])
        
        # Analyze if this should become a memory
        memory_analysis = self.personality.analyze_conversation_for_memory(
            user_query=query,
            assistant_response=response['content']
        )
        
        memory_stored = None
        if memory_analysis:
            print("\n💾 Storing new memory...")
            memory_id = self.personality.store_memory(
                content=memory_analysis['memory_content'],
                importance=memory_analysis['importance'],
                emotional_valence=memory_analysis['emotional_valence'],
                tags=memory_analysis['tags'],
                personality_impact=memory_analysis['personality_impact']
            )
            memory_stored = {
                "id": memory_id,
                "reason": memory_analysis['reason']
            }
            print(f"✅ Memory stored: {memory_id}")
            print(f"   Reason: {memory_analysis['reason']}\n")
        
        return {
            "query": query,
            "response": response['content'],
            "routing": routing,
            "model_used": response['model'],
            "memory_stored": memory_stored
        }
    
    def _execute_query(
        self, 
        query: str, 
        system_prompt: str,
        kb_context: str,
        conversation_history: list,
        routing_decision: dict
    ) -> dict:
        """Execute query with appropriate model"""
        model = routing_decision['model']
        
        if kb_context:
            enhanced_prompt = f"{system_prompt}\n\n{kb_context}"
        else:
            enhanced_prompt = system_prompt
        
        messages = [{"role": "system", "content": enhanced_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": query})
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7
            )
        except Exception as e:
            if "temperature" in str(e):
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=messages
                )
            else:
                raise
        
        return {
            "content": response.choices[0].message.content,
            "model": response.model
        }

def print_header():
    """Print header"""
    print("\n" + "=" * 80)
    print("🔍 ROOK - AI Investigative Journalist (Learning Mode)")
    print("=" * 80)
    print("\nI can now create and store new memories from our conversations!")
    print("\nWhat's new:")
    print("  • I analyze each conversation to see if it's worth remembering")
    print("  • Important insights are stored as new memories")
    print("  • I'll tell you when I create a new memory")
    print("  • These memories will influence future conversations")
    print("\nCommands:")
    print("  • Type your message and press Enter")
    print("  • Type 'exit' or 'quit' to end")
    print("  • Type 'memories' to see recent memories")
    print("=" * 80 + "\n")

def main():
    """Main chat loop"""
    print_header()
    
    try:
        rook = ROOKWithLearning(
            pinecone_api_key=PINECONE_API_KEY,
            openai_api_key=OPENAI_API_KEY
        )
    except Exception as e:
        print(f"\n❌ Error initializing ROOK: {e}")
        return
    
    print("\n✅ ROOK is ready! Start chatting...\n")
    
    user_id = "terminal_user"
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 ROOK: Thanks for the conversation. I'll remember what I learned!\n")
                break
            
            if user_input.lower() == 'memories':
                print("\n📚 Recent memories are stored in Pinecone.")
                print("   Use view_rook_memories.py to see them all.\n")
                continue
            
            # Process query
            result = rook.process_query(query=user_input, user_id=user_id)
            
            # Display response
            print(f"\n🔍 ROOK: {result['response']}\n")
            
            # Show if memory was stored
            if result['memory_stored']:
                print(f"💡 I stored this as a memory: {result['memory_stored']['reason']}\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 ROOK: Interrupted. I'll remember what I learned!\n")
            break
        
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    main()
