"""
ROOK Chat Server v2 - With Consciousness Architecture
Integrates hot cache, active reading, and background retrieval
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

# Import ROOK components
from src.personality.personality_layer_with_storage import PersonalityLayerWithStorage as PersonalityLayer
from src.consciousness import get_hot_cache, ActiveReader, BackgroundRetriever

app = FastAPI(title="ROOK Chat API v2", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ROOK components
print("🤖 Initializing ROOK v2...")

# Environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

if not OPENAI_API_KEY:
    print("⚠️  Warning: OPENAI_API_KEY not set")
if not PINECONE_API_KEY:
    print("⚠️  Warning: PINECONE_API_KEY not set")

# Initialize personality layer
personality_layer = PersonalityLayer(
    pinecone_api_key=PINECONE_API_KEY,
    openai_api_key=OPENAI_API_KEY
)

# Initialize consciousness components
hot_cache = get_hot_cache()
active_reader = ActiveReader(openai_api_key=OPENAI_API_KEY)
background_retriever = BackgroundRetriever(
    personality_layer=personality_layer,
    hot_cache=hot_cache,
    openai_api_key=OPENAI_API_KEY
)

print("✅ ROOK v2 initialized!")

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

class ReadingRequest(BaseModel):
    topics: Optional[List[str]] = None

class ReadingResponse(BaseModel):
    articles_read: int
    memories_created: List[Dict]
    summary: Dict

class CacheStatsResponse(BaseModel):
    cache_stats: Dict
    anticipation_stats: Dict
    reading_stats: Dict


@app.get("/")
async def root():
    """Serve the chat interface"""
    html_path = Path(__file__).parent.parent / "rook_chat.html"
    if html_path.exists():
        return FileResponse(html_path)
    return {"message": "ROOK Chat API v2", "status": "online"}


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "components": {
            "personality_layer": "online",
            "hot_cache": "online",
            "active_reader": "online",
            "background_retriever": "online"
        },
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with ROOK using consciousness architecture
    
    Flow:
    1. Check hot cache for instant response
    2. Start background retrieval for anticipated topics
    3. Generate response using personality layer
    4. Update hot cache
    5. Return response with metadata
    """
    try:
        user_message = request.message
        conversation_history = request.conversation_history or []
        
        # 1. Check hot cache first
        from_cache = False
        cached_response = hot_cache.get_cached(user_message)
        
        if cached_response and cached_response.get("content"):
            print(f"💨 Cache hit for: {user_message[:50]}...")
            from_cache = True
        
        # 2. Start background retrieval (non-blocking)
        anticipated_topics = background_retriever.anticipate_next_topics(
            user_message,
            conversation_history
        )
        
        # Note: In production, this would be truly async
        # For now, we'll just track the anticipated topics
        print(f"🔮 Anticipated next topics: {anticipated_topics}")
        
        # 3. Check if we have recent reading context
        reading_context = None
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
        
        # 6. Check anticipation accuracy (for next request)
        if len(conversation_history) > 0:
            last_user_msg = conversation_history[-1].get("content", "")
            if last_user_msg:
                accuracy = background_retriever.check_anticipation_accuracy(user_message)
                if accuracy:
                    print(f"✅ Correctly anticipated: {user_message[:50]}...")
        
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


@app.post("/api/read", response_model=ReadingResponse)
async def trigger_reading(request: ReadingRequest):
    """
    Trigger ROOK to read news
    
    This would normally be called by a cron job, but can be triggered manually
    """
    try:
        topics = request.topics
        
        # Read morning news
        memories = active_reader.read_morning_news(topics=topics)
        
        # Update hot cache with new readings
        hot_cache.refresh_cache(memories)
        
        # Get summary
        summary = active_reader.get_reading_summary(days=1)
        
        return ReadingResponse(
            articles_read=len(memories),
            memories_created=memories,
            summary=summary
        )
        
    except Exception as e:
        print(f"❌ Error during reading: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats", response_model=CacheStatsResponse)
async def get_stats():
    """Get consciousness system statistics"""
    try:
        cache_stats = hot_cache.get_cache_stats()
        anticipation_stats = background_retriever.get_anticipation_stats()
        reading_stats = active_reader.get_reading_summary(days=1)
        
        return CacheStatsResponse(
            cache_stats=cache_stats,
            anticipation_stats=anticipation_stats,
            reading_stats=reading_stats
        )
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/whats-on-my-mind")
async def whats_on_my_mind():
    """
    Get what's currently on ROOK's mind
    
    Returns immediate context from hot cache
    """
    try:
        context = hot_cache.get_immediate_context()
        return {
            "current_focus": context["current_focus"],
            "recent_thoughts": context["recent_thoughts"],
            "active_topics": context["active_topics"],
            "last_updated": context["last_updated"]
        }
    except Exception as e:
        print(f"❌ Error getting context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recent-readings")
async def recent_readings(limit: int = 10):
    """Get ROOK's recent readings"""
    try:
        readings = active_reader.get_recent_readings(limit=limit)
        return {
            "readings": readings,
            "count": len(readings)
        }
    except Exception as e:
        print(f"❌ Error getting readings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
