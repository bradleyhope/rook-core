"""
ROOK Chat API Server

FastAPI backend that connects the web interface to ROOK's Python system.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

from personality.personality_layer_with_storage import PersonalityLayerWithStorage
from routing.routing_engine import RoutingEngine
from knowledge.knowledge_base import KnowledgeBase
from openai import OpenAI

# API Keys
PINECONE_API_KEY = "YOUR_PINECONE_API_KEY"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# Initialize FastAPI
app = FastAPI(title="ROOK Chat API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "web_user"

class ChatResponse(BaseModel):
    response: str
    model_used: str
    memory_stored: Optional[dict] = None

# Global ROOK instance
rook = None

def get_rook():
    """Get or initialize ROOK instance"""
    global rook
    if rook is None:
        print("🤖 Initializing ROOK...")
        
        personality = PersonalityLayerWithStorage(
            pinecone_api_key=PINECONE_API_KEY,
            openai_api_key=OPENAI_API_KEY
        )
        
        router = RoutingEngine(openai_api_key=OPENAI_API_KEY)
        
        knowledge_base = KnowledgeBase(
            pinecone_api_key=PINECONE_API_KEY,
            openai_api_key=OPENAI_API_KEY
        )
        
        openai_client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url='https://api.openai.com/v1'
        )
        
        rook = {
            'personality': personality,
            'router': router,
            'knowledge_base': knowledge_base,
            'openai_client': openai_client
        }
        
        print("✅ ROOK initialized!")
    
    return rook

@app.get("/")
async def root():
    """Serve the chat interface"""
    return FileResponse(os.path.join(os.path.dirname(__file__), '..', 'rook_chat.html'))

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ROOK Chat API"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message through ROOK's full system.
    """
    try:
        rook_system = get_rook()
        
        # Enrich with personality and memories
        enriched = rook_system['personality'].enrich_query(
            request.message, 
            request.user_id
        )
        system_prompt = enriched["system_prompt"]
        conversation_history = enriched["conversation_history"]
        
        # Route the query
        routing = rook_system['router'].route_query(request.message, system_prompt)
        query_type = routing['analysis'].get('query_type', 'simple_chat')
        
        # Get knowledge base context
        kb_context = rook_system['knowledge_base'].get_context_for_query(
            request.message, 
            query_type
        )
        
        # Build messages
        if kb_context:
            enhanced_prompt = f"{system_prompt}\n\n{kb_context}"
        else:
            enhanced_prompt = system_prompt
        
        messages = [{"role": "system", "content": enhanced_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": request.message})
        
        # Get response from OpenAI
        model = routing['routing_decision']['model']
        
        try:
            response = rook_system['openai_client'].chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7
            )
        except Exception as e:
            if "temperature" in str(e):
                response = rook_system['openai_client'].chat.completions.create(
                    model=model,
                    messages=messages
                )
            else:
                raise
        
        assistant_response = response.choices[0].message.content
        
        # Update conversation history
        rook_system['personality'].add_to_conversation_history(
            request.user_id, "user", request.message
        )
        rook_system['personality'].add_to_conversation_history(
            request.user_id, "assistant", assistant_response
        )
        
        # Analyze if should store memory
        memory_analysis = rook_system['personality'].analyze_conversation_for_memory(
            user_query=request.message,
            assistant_response=assistant_response
        )
        
        memory_stored = None
        if memory_analysis:
            print(f"💾 Storing new memory...")
            memory_id = rook_system['personality'].store_memory(
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
        
        # Don't expose memory storage to user - it's internal
        return ChatResponse(
            response=assistant_response,
            model_used=response.model,
            memory_stored=None  # Keep this internal
        )
    
    except Exception as e:
        print(f"❌ Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("=" * 80)
    print("🔍 Starting ROOK Chat API Server")
    print("=" * 80)
    print()
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8080,
        log_level="info"
    )
