from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StyleUploadRequest(BaseModel):
    """Request model for style upload"""
    images: List[str]  # base64 encoded images
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    category: Optional[str] = None  # "casual", "business", "formal", "sport"

class StyleResponse(BaseModel):
    """Response model for style data"""
    style_id: str
    image_urls: List[str]
    tags: List[str]
    embeddings: Optional[List[List[float]]] = None
    created_at: datetime
    description: Optional[str] = None
    category: Optional[str] = None
    similarity_scores: Optional[List[float]] = None  # For style matching results
