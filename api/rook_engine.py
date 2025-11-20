"""
ROOK Engine - Core Intelligence Service
Internal API for ROOK's consciousness and personality

This service runs continuously and maintains:
- Hot cache (fast working memory)
- Personality layer (Pinecone-backed)
- Active reader (news ingestion)
- Background retriever (anticipatory pre-fetching)

Designed to be called by rook-web or other client services.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
from datetime import datetime

# Import ROOK components
from src.personality.personality_layer_with_storage import PersonalityLayerWithStorage as PersonalityLayer
from src.consciousness import get_hot_cache, ActiveReader, BackgroundRetriever

app = FastAPI(
    title="ROOK Engine API",
    version="1.0.0",
    description="Core ROOK intelligence service - Internal API only"
)

# CORS - restrict to internal services in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to rook-web service URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
ENGINE_API_KEY = os.getenv('ENGINE_API_KEY', 'dev-key-change-in-production')

# Track initialization status
initialization_status = {
    "personality_layer": "not_initialized",
    "hot_cache": "not_initialized",
    "active_reader": "not_initialized",
    "background_retriever": "not_initialized",
    "errors": [],
    "initialized_at": None
}

# Initialize components
personality_layer = None
hot_cache = None
active_reader = None
background_retriever = None

print("🧠 Initializing ROOK Engine...")

# Check environment variables
if not OPENAI_API_KEY:
    msg = "⚠️  OPENAI_API_KEY not set"
    print(msg)
    initialization_status["errors"].append(msg)
else:
    print("✅ OPENAI_API_KEY found")

if not PINECONE_API_KEY:
    msg = "⚠️  PINECONE_API_KEY not set"
    print(msg)
    initialization_status["errors"].append(msg)
else:
    print("✅ PINECONE_API_KEY found")

if not NEWSAPI_KEY:
    msg = "ℹ️  NEWSAPI_KEY not set - News reading will be disabled (optional)"
    print(msg)

# Initialize personality layer
if PINECONE_API_KEY and OPENAI_API_KEY:
    try:
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

# Initialize consciousness components
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

initialization_status["initialized_at"] = datetime.now().isoformat()
print(f"🚀 ROOK Engine ready: {initialization_status}")


# Security: Simple API key authentication
def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key for internal service authentication"""
    if x_api_key != ENGINE_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict]] = []
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    model_used: str
    from_cache: bool = False
    anticipated_topics: Optional[List[str]] = None
    reading_context: Optional[str] = None
    timestamp: str

class ReadingRequest(BaseModel):
    topics: Optional[List[str]] = None

class MemoryQuery(BaseModel):
    query: str
    limit: int = 5
    namespace: Optional[str] = None


@app.get("/")
async def root():
    """Engine status"""
    return {
        "service": "ROOK Engine",
        "version": "1.0.0",
        "status": "online",
        "note": "Internal API - use /health for status check"
    }


@app.get("/health")
async def health():
    """Health check - no auth required"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "components": initialization_status,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, api_key: str = Header(None, alias="X-API-Key")):
    """
    Generate ROOK response using full consciousness architecture
    
    Requires X-API-Key header for authentication
    """
    verify_api_key(api_key)
    
    try:
        if not personality_layer:
            raise HTTPException(
                status_code=503,
                detail="ROOK Engine not fully initialized. Check /health for details."
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
                        "timestamp": datetime.now().isoformat(),
                        "user_id": request.user_id
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
            reading_context=reading_context,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error processing chat: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/read")
async def trigger_reading(request: ReadingRequest, api_key: str = Header(None, alias="X-API-Key")):
    """
    Trigger ROOK to read news
    
    Requires X-API-Key header for authentication
    """
    verify_api_key(api_key)
    
    try:
        if not active_reader:
            raise HTTPException(status_code=503, detail="Active reader not initialized")
        
        topics = request.topics
        memories = active_reader.read_morning_news(topics=topics)
        
        # Update hot cache with new readings
        if hot_cache:
            hot_cache.refresh_cache(memories)
        
        summary = active_reader.get_reading_summary(days=1)
        
        return {
            "articles_read": len(memories),
            "memories_created": memories,
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error during reading: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/context")
async def get_context(api_key: str = Header(None, alias="X-API-Key")):
    """
    Get ROOK's current mental context (what's on his mind)
    
    Requires X-API-Key header for authentication
    """
    verify_api_key(api_key)
    
    try:
        if not hot_cache:
            raise HTTPException(status_code=503, detail="Hot cache not initialized")
        
        context = hot_cache.get_immediate_context()
        return {
            "current_focus": context["current_focus"],
            "recent_thoughts": context["recent_thoughts"],
            "active_topics": context["active_topics"],
            "last_updated": context["last_updated"],
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/memory/query")
async def query_memory(request: MemoryQuery, api_key: str = Header(None, alias="X-API-Key")):
    """
    Query ROOK's memory systems
    
    Requires X-API-Key header for authentication
    """
    verify_api_key(api_key)
    
    try:
        if not personality_layer:
            raise HTTPException(status_code=503, detail="Personality layer not initialized")
        
        # Query personality/memory layer
        results = personality_layer.query_memory(
            query=request.query,
            top_k=request.limit,
            namespace=request.namespace
        )
        
        return {
            "query": request.query,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error querying memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats(api_key: str = Header(None, alias="X-API-Key")):
    """
    Get consciousness system statistics
    
    Requires X-API-Key header for authentication
    """
    verify_api_key(api_key)
    
    try:
        stats = {
            "cache_stats": hot_cache.get_cache_stats() if hot_cache else {},
            "anticipation_stats": background_retriever.get_anticipation_stats() if background_retriever else {},
            "reading_stats": active_reader.get_reading_summary(days=1) if active_reader else {},
            "timestamp": datetime.now().isoformat()
        }
        return stats
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    print(f"🚀 Starting ROOK Engine on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
