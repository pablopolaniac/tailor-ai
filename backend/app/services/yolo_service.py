import cv2
import numpy as np
from typing import List, Dict, Any
from ultralytics import YOLO
import io
from PIL import Image

from app.core.config import settings

class YOLOService:
    """YOLOv8 service for garment and body detection"""
    
    def __init__(self):
        self.model = None
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
        
        # Fashion-specific classes
        self.fashion_classes = [
            "person", "shirt", "pants", "dress", "skirt", "jacket", 
            "shoes", "bag", "hat", "glasses", "watch"
        ]
    
    async def load_model(self):
        """Load YOLOv8 model"""
        try:
            print("Loading YOLOv8 model...")
            self.model = YOLO(settings.YOLO_MODEL_PATH)
            print("YOLOv8 model loaded successfully")
        except Exception as e:
            print(f"Error loading YOLOv8 model: {e}")
            # Fallback to mock model for development
            self.model = None
    
    async def detect_objects(self, frame: bytes) -> List[Dict[str, Any]]:
        """Detect objects in frame"""
        try:
            if self.model is None:
                return await self._mock_detection(frame)
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(frame))
            
            # Run YOLO detection
            results = self.model(image, conf=self.confidence_threshold)
            
            detections = []
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        
                        # Get class and confidence
                        class_id = int(box.cls[0].cpu().numpy())
                        confidence = float(box.conf[0].cpu().numpy())
                        
                        # Get class name
                        class_name = self.model.names[class_id]
                        
                        # Only include fashion-relevant detections
                        if class_name in self.fashion_classes:
                            detections.append({
                                "bbox": [int(x1), int(y1), int(x2), int(y2)],
                                "class": class_name,
                                "confidence": confidence,
                                "class_id": class_id
                            })
            
            return detections
            
        except Exception as e:
            print(f"Error in YOLO detection: {e}")
            return await self._mock_detection(frame)
    
    async def _mock_detection(self, frame: bytes) -> List[Dict[str, Any]]:
        """Mock detection for development"""
        return [
            {
                "bbox": [100, 100, 300, 400],
                "class": "person",
                "confidence": 0.95,
                "class_id": 0
            },
            {
                "bbox": [120, 150, 280, 350],
                "class": "shirt",
                "confidence": 0.87,
                "class_id": 1
            },
            {
                "bbox": [130, 350, 270, 500],
                "class": "pants",
                "confidence": 0.82,
                "class_id": 2
            }
        ]
    
    async def detect_body_keypoints(self, frame: bytes) -> List[Dict[str, Any]]:
        """Detect body keypoints for pose estimation"""
        try:
            if self.model is None:
                return await self._mock_keypoints()
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(frame))
            
            # Run pose estimation
            results = self.model(image, conf=self.confidence_threshold)
            
            keypoints = []
            for result in results:
                if hasattr(result, 'keypoints') and result.keypoints is not None:
                    kpts = result.keypoints.data[0].cpu().numpy()
                    
                    for i, kpt in enumerate(kpts):
                        if kpt[2] > self.confidence_threshold:  # visibility > threshold
                            keypoints.append({
                                "x": float(kpt[0]),
                                "y": float(kpt[1]),
                                "confidence": float(kpt[2]),
                                "keypoint_id": i
                            })
            
            return keypoints
            
        except Exception as e:
            print(f"Error in keypoint detection: {e}")
            return await self._mock_keypoints()
    
    async def _mock_keypoints(self) -> List[Dict[str, Any]]:
        """Mock keypoints for development"""
        return [
            {"x": 200, "y": 150, "confidence": 0.9, "keypoint_id": 0},  # nose
            {"x": 200, "y": 200, "confidence": 0.85, "keypoint_id": 5},  # left shoulder
            {"x": 200, "y": 200, "confidence": 0.85, "keypoint_id": 6},  # right shoulder
            {"x": 200, "y": 300, "confidence": 0.8, "keypoint_id": 11},  # left hip
            {"x": 200, "y": 300, "confidence": 0.8, "keypoint_id": 12},  # right hip
        ]
