"""
ROOK Chat Server v2 - Safe Startup Version
Gracefully handles missing environment variables
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
from datetime import datetime

app = FastAPI(title="ROOK Chat API v2", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')

# Track initialization status
initialization_status = {
    "personality_layer": "not_initialized",
    "hot_cache": "not_initialized",
    "active_reader": "not_initialized",
    "background_retriever": "not_initialized",
    "errors": []
}

# Try to initialize components
personality_layer = None
hot_cache = None
active_reader = None
background_retriever = None

print("🤖 Initializing ROOK v2 (Safe Mode)...")

# Check environment variables
if not OPENAI_API_KEY:
    msg = "⚠️  OPENAI_API_KEY not set - AI features will be limited"
    print(msg)
    initialization_status["errors"].append(msg)
else:
    print("✅ OPENAI_API_KEY found")

if not PINECONE_API_KEY:
    msg = "⚠️  PINECONE_API_KEY not set - Memory features will be limited"
    print(msg)
    initialization_status["errors"].append(msg)
else:
    print("✅ PINECONE_API_KEY found")

if not NEWSAPI_KEY:
    msg = "ℹ️  NEWSAPI_KEY not set - News reading will be disabled (optional)"
    print(msg)
    initialization_status["errors"].append(msg)

# Try to initialize personality layer
if PINECONE_API_KEY and OPENAI_API_KEY:
    try:
        from src.personality.personality_layer_with_storage import PersonalityLayerWithStorage as PersonalityLayer
        personality_layer = PersonalityLayer(
            pinecone_api_key=PINECONE_API_KEY,
            openai_api_key=OPENAI_API_KEY
        )
        initialization_status["personality_layer"] = "online"
        print("✅ Personality layer initialized")
    except Exception as e:
        msg = f"❌ Personality layer failed: {e}"
        print(msg)
        initialization_status["personality_layer"] = "failed"
        initialization_status["errors"].append(msg)

# Try to initialize consciousness components
try:
    from src.consciousness import get_hot_cache, ActiveReader, BackgroundRetriever
    
    hot_cache = get_hot_cache()
    initialization_status["hot_cache"] = "online"
    print("✅ Hot cache initialized")
    
    if OPENAI_API_KEY:
        active_reader = ActiveReader(openai_api_key=OPENAI_API_KEY, newsapi_key=NEWSAPI_KEY)
        initialization_status["active_reader"] = "online"
        print("✅ Active reader initialized")
    
    if personality_layer and hot_cache and OPENAI_API_KEY:
        background_retriever = BackgroundRetriever(
            personality_layer=personality_layer,
            hot_cache=hot_cache,
            openai_api_key=OPENAI_API_KEY
        )
        initialization_status["background_retriever"] = "online"
        print("✅ Background retriever initialized")
        
except Exception as e:
    msg = f"❌ Consciousness modules failed: {e}"
    print(msg)
    initialization_status["errors"].append(msg)

print(f"🚀 ROOK v2 started with status: {initialization_status}")

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict]] = []

class ChatResponse(BaseModel):
    response: str
    model_used: str
    from_cache: bool = False
    anticipated_topics: Optional[List[str]] = None
    reading_context: Optional[str] = None


@app.get("/")
async def root():
    """Serve the chat interface"""
    html_path = Path(__file__).parent.parent / "rook_chat.html"
    if html_path.exists():
        return FileResponse(html_path)
    return {
        "message": "ROOK Chat API v2",
        "status": "online",
        "initialization": initialization_status
    }


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "components": initialization_status,
        "environment": {
            "OPENAI_API_KEY": "set" if OPENAI_API_KEY else "missing",
            "PINECONE_API_KEY": "set" if PINECONE_API_KEY else "missing",
            "NEWSAPI_KEY": "set" if NEWSAPI_KEY else "missing"
        },
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with ROOK using consciousness architecture
    """
    try:
        # Check if we have the required components
        if not personality_layer:
            return ChatResponse(
                response="ROOK is not fully initialized. Missing required environment variables: OPENAI_API_KEY and/or PINECONE_API_KEY. Please set these in your Render dashboard.",
                model_used="error",
                from_cache=False
            )
        
        user_message = request.message
        conversation_history = request.conversation_history or []
        
        # 1. Check hot cache first
        from_cache = False
        if hot_cache:
            cached_response = hot_cache.get_cached(user_message)
            if cached_response and cached_response.get("content"):
                print(f"💨 Cache hit for: {user_message[:50]}...")
                from_cache = True
        
        # 2. Start background retrieval (non-blocking)
        anticipated_topics = []
        if background_retriever:
            anticipated_topics = background_retriever.anticipate_next_topics(
                user_message,
                conversation_history
            )
            print(f"🔮 Anticipated next topics: {anticipated_topics}")
        
        # 3. Check if we have recent reading context
        reading_context = None
        if active_reader:
            recent_readings = active_reader.get_recent_readings(limit=3)
            if recent_readings:
                reading_context = f"Recently read: {', '.join([r['title'][:50] for r in recent_readings])}"
        
        # 4. Generate response using personality layer
        if not from_cache:
            response_text, model_used = personality_layer.chat(
                user_message=user_message,
                conversation_history=conversation_history
            )
            
            # 5. Update hot cache
            if hot_cache:
                hot_cache.update_context(
                    topic=user_message,
                    content=response_text,
                    metadata={
                        "model": model_used,
                        "timestamp": datetime.now().isoformat()
                    }
                )
        else:
            response_text = cached_response["content"]
            model_used = cached_response.get("metadata", {}).get("model", "cache")
        
        return ChatResponse(
            response=response_text,
            model_used=model_used,
            from_cache=from_cache,
            anticipated_topics=anticipated_topics,
            reading_context=reading_context
        )
        
    except Exception as e:
        print(f"❌ Error processing chat: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def get_status():
    """Get detailed initialization status"""
    return {
        "initialization": initialization_status,
        "components_ready": {
            "personality_layer": personality_layer is not None,
            "hot_cache": hot_cache is not None,
            "active_reader": active_reader is not None,
            "background_retriever": background_retriever is not None
        },
        "environment_variables": {
            "OPENAI_API_KEY": "✅ Set" if OPENAI_API_KEY else "❌ Missing",
            "PINECONE_API_KEY": "✅ Set" if PINECONE_API_KEY else "❌ Missing",
            "NEWSAPI_KEY": "✅ Set" if NEWSAPI_KEY else "⚠️  Not set (optional)"
        }
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting ROOK v2 on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
