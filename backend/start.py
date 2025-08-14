#!/usr/bin/env python3
"""
Simple startup script for TailorAI backend
This script sets up basic environment and starts the server
"""

import os
import sys
from pathlib import Path

# Set up basic environment variables if not already set
os.environ.setdefault('DATABASE_URL', 'sqlite:///./tailorai.db')
os.environ.setdefault('OPENAI_API_KEY', 'your_openai_api_key_here')
os.environ.setdefault('YOLO_MODEL_PATH', 'yolov8n.pt')
os.environ.setdefault('CLIP_MODEL_NAME', 'openai/clip-vit-base-patch32')
os.environ.setdefault('API_V1_STR', '/api/v1')
os.environ.setdefault('PROJECT_NAME', 'TailorAI')
os.environ.setdefault('FRAME_SAMPLE_RATE', '5')
os.environ.setdefault('CONFIDENCE_THRESHOLD', '0.5')
os.environ.setdefault('MAX_FRAMES_PER_REQUEST', '10')
os.environ.setdefault('MAX_STYLE_IMAGES', '5')
os.environ.setdefault('SIMILARITY_THRESHOLD', '0.7')

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting TailorAI Backend (OpenAI Vision Only)...")
    print("📝 Note: Set OPENAI_API_KEY in environment for full functionality")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("⚡ Lightweight backend - no heavy AI models to load!")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
