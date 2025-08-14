from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import base64
import json
from typing import List, Optional
import asyncio

from app.core.config import settings
from app.core.database import engine, Base
from app.models import style_models, user_models
from app.services.ai_orchestrator import AIOrchestrator
from app.services.storage_service import StorageService
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.schemas.style import StyleUploadRequest, StyleResponse

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TailorAI API",
    description="AI-Powered Fashion Analysis API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://tailorai.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
storage_service = StorageService()

@app.get("/")
async def root():
    return {"message": "TailorAI API is running"}

@app.post("/api/analyze")
async def analyze_fashion(request: AnalysisRequest):
    """Analyze fashion from uploaded image"""
    try:
        # Use AI orchestrator to analyze the frame
        result = AIOrchestrator.analyze_frame(
            mode=request.mode,
            frame_b64=request.frame_b64,
            season=request.season,  # Pass season to AI orchestrator
            style_profile=request.style_profile
        )
        
        # Add frame count for tracking
        result["frame_count"] = 1
        
        return result
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@app.post("/api/v1/upload-style", response_model=StyleResponse)
async def upload_style(
    images: List[UploadFile] = File(...),
    tags: Optional[str] = Form(None)
):
    """
    Upload reference style images
    """
    try:
        # Parse tags
        tag_list = json.loads(tags) if tags else []
        
        # Upload images to cloud storage
        image_urls = []
        for image in images:
            url = await storage_service.upload_image(image)
            image_urls.append(url)
        
        # Generate style ID (simplified - no embeddings for now)
        import time
        style_id = f"style_{int(time.time())}"
        
        return StyleResponse(
            style_id=style_id,
            image_urls=image_urls,
            tags=tag_list
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Style upload failed: {str(e)}")

@app.get("/api/v1/styles/{style_id}", response_model=StyleResponse)
async def get_style(style_id: str):
    """
    Retrieve style information
    """
    try:
        # Mock style data (simplified)
        import time
        style_data = {
            "style_id": style_id,
            "image_urls": [],
            "tags": [],
            "embeddings": [],
            "created_at": time.time(),
            "description": "Mock style",
            "category": "casual"
        }
        return StyleResponse(**style_data)
    
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Style not found: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "ai_service": "openai_vision"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
