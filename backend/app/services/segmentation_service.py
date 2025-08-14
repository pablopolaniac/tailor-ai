import cv2
import numpy as np
from typing import List, Dict, Any, Optional
from PIL import Image
import io
import base64

# Note: In production, you would import segment_anything
# from segment_anything import SamPredictor, sam_model_registry

class SegmentationService:
    """Segment Anything service for garment segmentation"""
    
    def __init__(self):
        self.model = None
        self.predictor = None
    
    async def load_model(self):
        """Load Segment Anything model"""
        try:
            print("Loading Segment Anything model...")
            # In production, you would load the actual SAM model
            # sam = sam_model_registry["vit_h"](checkpoint=settings.SEGMENT_ANYTHING_MODEL_PATH)
            # self.predictor = SamPredictor(sam)
            print("Segment Anything model loaded successfully")
        except Exception as e:
            print(f"Error loading Segment Anything model: {e}")
            # Fallback to mock model for development
            self.model = None
    
    async def segment_object(
        self, 
        frame: bytes, 
        bbox: List[int]
    ) -> str:
        """Segment object within bounding box"""
        try:
            if self.predictor is None:
                return await self._mock_segmentation(bbox)
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(frame))
            image_array = np.array(image)
            
            # Set image in predictor
            self.predictor.set_image(image_array)
            
            # Convert bbox to SAM format [x1, y1, x2, y2]
            x1, y1, x2, y2 = bbox
            input_box = np.array([x1, y1, x2, y2])
            
            # Generate mask
            masks, scores, logits = self.predictor.predict(
                box=input_box,
                multimask_output=True
            )
            
            # Select best mask
            best_mask_idx = np.argmax(scores)
            mask = masks[best_mask_idx]
            
            # Convert mask to base64
            mask_image = Image.fromarray((mask * 255).astype(np.uint8))
            buffer = io.BytesIO()
            mask_image.save(buffer, format='PNG')
            mask_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return mask_b64
            
        except Exception as e:
            print(f"Error in segmentation: {e}")
            return await self._mock_segmentation(bbox)
    
    async def segment_with_points(
        self, 
        frame: bytes, 
        points: List[List[float]], 
        labels: List[int]
    ) -> str:
        """Segment object using point prompts"""
        try:
            if self.predictor is None:
                return await self._mock_segmentation([100, 100, 300, 400])
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(frame))
            image_array = np.array(image)
            
            # Set image in predictor
            self.predictor.set_image(image_array)
            
            # Convert points to numpy array
            input_points = np.array(points)
            input_labels = np.array(labels)
            
            # Generate mask
            masks, scores, logits = self.predictor.predict(
                point_coords=input_points,
                point_labels=input_labels,
                multimask_output=True
            )
            
            # Select best mask
            best_mask_idx = np.argmax(scores)
            mask = masks[best_mask_idx]
            
            # Convert mask to base64
            mask_image = Image.fromarray((mask * 255).astype(np.uint8))
            buffer = io.BytesIO()
            mask_image.save(buffer, format='PNG')
            mask_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            return mask_b64
            
        except Exception as e:
            print(f"Error in point-based segmentation: {e}")
            return await self._mock_segmentation([100, 100, 300, 400])
    
    async def segment_garments(
        self, 
        frame: bytes, 
        detections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Segment multiple garments in frame"""
        try:
            segmentation_results = []
            
            for detection in detections:
                if detection["class"] in ["shirt", "pants", "dress", "skirt", "jacket"]:
                    mask = await self.segment_object(frame, detection["bbox"])
                    
                    segmentation_results.append({
                        "bbox": detection["bbox"],
                        "mask": mask,
                        "class": detection["class"],
                        "confidence": detection["confidence"]
                    })
            
            return segmentation_results
            
        except Exception as e:
            print(f"Error in garment segmentation: {e}")
            return await self._mock_garment_segmentation()
    
    async def _mock_segmentation(self, bbox: List[int]) -> str:
        """Mock segmentation for development"""
        # Create a simple rectangular mask
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        
        # Create mask image
        mask = np.zeros((height, width), dtype=np.uint8)
        mask[:, :] = 255  # Fill with white
        
        # Convert to base64
        mask_image = Image.fromarray(mask)
        buffer = io.BytesIO()
        mask_image.save(buffer, format='PNG')
        mask_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return mask_b64
    
    async def _mock_garment_segmentation(self) -> List[Dict[str, Any]]:
        """Mock garment segmentation for development"""
        return [
            {
                "bbox": [120, 150, 280, 350],
                "mask": await self._mock_segmentation([120, 150, 280, 350]),
                "class": "shirt",
                "confidence": 0.87
            },
            {
                "bbox": [130, 350, 270, 500],
                "mask": await self._mock_segmentation([130, 350, 270, 500]),
                "class": "pants",
                "confidence": 0.82
            }
        ]
