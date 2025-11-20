"""
ROOK Web - Public API Gateway
Handles external requests and forwards to rook-engine

This service:
- Serves the web chat interface
- Validates and rate-limits requests
- Calls rook-engine for ROOK intelligence
- Logs conversations to database
- Handles authentication (future)
"""

import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn
from datetime import datetime
from pathlib import Path

app = FastAPI(
    title="ROOK Chat API",
    version="1.0.0",
    description="Public API for ROOK AI Investigative Journalist"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
ROOK_ENGINE_URL = os.getenv('ROOK_ENGINE_URL', 'http://localhost:8001')
ENGINE_API_KEY = os.getenv('ENGINE_API_KEY', 'dev-key-change-in-production')
DATABASE_URL = os.getenv('DATABASE_URL')

print(f"🌐 ROOK Web starting...")
print(f"📡 Engine URL: {ROOK_ENGINE_URL}")
print(f"🔑 Engine API Key: {'Set' if ENGINE_API_KEY else 'Not set'}")
print(f"💾 Database: {'Connected' if DATABASE_URL else 'Not configured'}")


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
        "message": "ROOK Chat API",
        "version": "1.0.0",
        "status": "online",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check - also checks engine connectivity"""
    
    # Check if engine is reachable
    engine_status = "unknown"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{ROOK_ENGINE_URL}/health")
            if response.status_code == 200:
                engine_status = "online"
                engine_data = response.json()
            else:
                engine_status = "error"
                engine_data = {"error": f"Status code {response.status_code}"}
    except Exception as e:
        engine_status = "unreachable"
        engine_data = {"error": str(e)}
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "rook-web",
        "engine": {
            "url": ROOK_ENGINE_URL,
            "status": engine_status,
            "details": engine_data if engine_status == "online" else {"error": engine_data.get("error")}
        },
        "database": "connected" if DATABASE_URL else "not_configured",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with ROOK
    
    This endpoint forwards the request to rook-engine and returns the response.
    In the future, this will also:
    - Authenticate users
    - Rate limit requests
    - Log conversations to database
    - Track usage analytics
    """
    try:
        # TODO: Add rate limiting
        # TODO: Add user authentication
        # TODO: Log conversation to database
        
        # Forward request to rook-engine
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ROOK_ENGINE_URL}/api/chat",
                json={
                    "message": request.message,
                    "conversation_history": request.conversation_history
                },
                headers={"X-API-Key": ENGINE_API_KEY}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Engine error: {response.text}"
                )
            
            engine_response = response.json()
        
        # TODO: Save conversation to database
        
        return ChatResponse(**engine_response)
        
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="ROOK is thinking too hard (timeout). Please try again."
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="ROOK engine is not reachable. Please try again later."
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/whats-on-my-mind")
async def whats_on_my_mind():
    """
    Get what's currently on ROOK's mind
    
    Returns immediate context from ROOK's hot cache
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{ROOK_ENGINE_URL}/api/context",
                headers={"X-API-Key": ENGINE_API_KEY}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Engine error: {response.text}"
                )
            
            return response.json()
            
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="ROOK engine is not reachable"
        )
    except Exception as e:
        print(f"❌ Error getting context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_stats():
    """Get ROOK's consciousness statistics"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{ROOK_ENGINE_URL}/api/stats",
                headers={"X-API-Key": ENGINE_API_KEY}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Engine error: {response.text}"
                )
            
            return response.json()
            
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="ROOK engine is not reachable"
        )
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/trigger-reading")
async def trigger_reading(topics: Optional[List[str]] = None):
    """
    Trigger ROOK to read news
    
    This is a convenience endpoint for manual triggering.
    In production, this would be called by a cron job.
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{ROOK_ENGINE_URL}/api/read",
                json={"topics": topics},
                headers={"X-API-Key": ENGINE_API_KEY}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Engine error: {response.text}"
                )
            
            return response.json()
            
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="ROOK engine is not reachable"
        )
    except Exception as e:
        print(f"❌ Error triggering reading: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not found",
            "message": "The requested endpoint does not exist",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "Something went wrong. Please try again later."
        }
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting ROOK Web on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
