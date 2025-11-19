"""
ROOK API - FastAPI application for AI investigative journalist
"""
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from rook_enhanced import ROOK

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ROOK AI Investigative Journalist",
    description="An AI system with emergent personality for investigative journalism",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ROOK instance
rook = None

@app.on_event("startup")
async def startup_event():
    """Initialize ROOK on startup"""
    global rook
    try:
        logger.info("Initializing ROOK...")
        
        # Check required environment variables
        required_vars = ["OPENAI_API_KEY", "PINECONE_API_KEY", "PINECONE_ENVIRONMENT"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            raise ValueError(f"Missing environment variables: {missing_vars}")
        
        rook = ROOK()
        logger.info("ROOK initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ROOK: {e}")
        raise

# Request/Response models
class InvestigationRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class InvestigationResponse(BaseModel):
    investigation_id: str
    response: str
    method_card: Optional[Dict[str, Any]] = None
    moves_ledger: Optional[Dict[str, Any]] = None
    verification_score: Optional[float] = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ROOK AI Investigative Journalist",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "rook_initialized": rook is not None,
        "database": "connected" if os.getenv("DATABASE_URL") else "not configured"
    }

@app.post("/investigate", response_model=InvestigationResponse)
async def investigate(request: InvestigationRequest):
    """
    Main investigation endpoint
    
    Accepts a query and optional context, returns ROOK's investigation results
    with full transparency (method card and moves ledger)
    """
    if rook is None:
        raise HTTPException(status_code=503, detail="ROOK not initialized")
    
    try:
        logger.info(f"Processing investigation request: {request.query[:100]}...")
        
        # Process investigation through ROOK
        result = rook.investigate(
            query=request.query,
            context=request.context or {}
        )
        
        return InvestigationResponse(
            investigation_id=result.get("investigation_id", "unknown"),
            response=result.get("response", ""),
            method_card=result.get("method_card"),
            moves_ledger=result.get("moves_ledger"),
            verification_score=result.get("verification_score")
        )
    
    except Exception as e:
        logger.error(f"Investigation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/personality")
async def get_personality():
    """Get information about ROOK's current personality state"""
    if rook is None:
        raise HTTPException(status_code=503, detail="ROOK not initialized")
    
    try:
        # Get personality information from ROOK
        personality_info = {
            "status": "emergent",
            "description": "ROOK's personality emerges from formative memories and experiences",
            "memory_count": "stored in Pinecone"
        }
        return personality_info
    except Exception as e:
        logger.error(f"Failed to get personality info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
