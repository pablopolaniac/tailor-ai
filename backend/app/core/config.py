from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./tailorai.db"
    
    # AI Models
    OPENAI_API_KEY: str
    YOLO_MODEL_PATH: str = "yolov8n.pt"
    CLIP_MODEL_NAME: str = "openai/clip-vit-base-patch32"
    SEGMENT_ANYTHING_MODEL_PATH: str = "sam_vit_h_4b8939.pth"
    
    # Cloud Storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: str = "tailorai-images"
    AWS_REGION: str = "us-east-1"
    
    # Alternative: Google Cloud Storage
    GCS_BUCKET_NAME: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # Redis for caching
    REDIS_URL: str = "redis://localhost:6379"
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TailorAI"
    
    # Model Settings
    FRAME_SAMPLE_RATE: int = 5  # Process every 5th frame
    CONFIDENCE_THRESHOLD: float = 0.5
    MAX_FRAMES_PER_REQUEST: int = 10
    
    # Style Analysis
    MAX_STYLE_IMAGES: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
