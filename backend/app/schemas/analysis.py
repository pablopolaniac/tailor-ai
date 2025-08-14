from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class UserPreferences(BaseModel):
    """User preferences for fashion analysis"""
    style_preferences: Optional[List[str]] = None
    color_preferences: Optional[List[str]] = None
    fit_preferences: Optional[str] = None  # "loose", "fitted", "oversized"
    occasion: Optional[str] = None  # "casual", "business", "formal", "sport"
    body_type: Optional[str] = None
    age_group: Optional[str] = None

class AnalysisMode(str, Enum):
    general = "general"
    style = "style"

class Season(str, Enum):
    spring = "spring"
    summer = "summer"
    autumn = "autumn"
    winter = "winter"

class AnalysisRequest(BaseModel):
    mode: AnalysisMode = Field(..., description="Analysis mode: general or style")
    frame_b64: str = Field(..., description="Base64 encoded image frame")
    season: Season = Field(default=Season.summer, description="Current season for context-aware recommendations")
    style_profile: Optional[Dict[str, Any]] = Field(None, description="Style profile for style matching mode")

class FeedbackItem(BaseModel):
    """Individual feedback item"""
    type: str  # "proportion", "color", "style", "fit", "general"
    message: str
    confidence: float
    priority: str  # "high", "medium", "low"
    actionable: bool = True

class OverlayData(BaseModel):
    """Data for visual overlay"""
    bounding_boxes: List[Dict[str, Any]] = []
    keypoints: List[Dict[str, Any]] = []
    segmentation_masks: List[str] = []  # base64 encoded masks
    guide_lines: List[Dict[str, Any]] = []
    color_analysis: Optional[Dict[str, Any]] = None

class AnalysisResponse(BaseModel):
    """Response model for fashion analysis"""
    feedback: List[FeedbackItem]
    overlay_data: OverlayData
    confidence_score: float
    processing_time: Optional[float] = None
    frame_count: int
