import torch
import numpy as np
from typing import List, Dict, Any, Optional
from transformers import CLIPProcessor, CLIPModel
import requests
from PIL import Image
import io
import base64

from app.core.config import settings

class CLIPService:
    """CLIP service for style embeddings and similarity scoring"""
    
    def __init__(self):
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
    
    async def load_model(self):
        """Load CLIP model"""
        try:
            print("Loading CLIP model...")
            self.model = CLIPModel.from_pretrained(settings.CLIP_MODEL_NAME)
            self.processor = CLIPProcessor.from_pretrained(settings.CLIP_MODEL_NAME)
            
            self.model.to(self.device)
            self.model.eval()
            print("CLIP model loaded successfully")
        except Exception as e:
            print(f"Error loading CLIP model: {e}")
            # Fallback to mock model for development
            self.model = None
    
    async def encode_image(self, image_input: str) -> List[float]:
        """Encode image to CLIP embedding"""
        try:
            if self.model is None:
                return await self._mock_embedding()
            
            # Handle different input types
            if image_input.startswith('http'):
                # Download image from URL
                response = requests.get(image_input)
                image = Image.open(io.BytesIO(response.content))
            elif image_input.startswith('data:image'):
                # Base64 encoded image
                image_data = image_input.split(',')[1]
                image = Image.open(io.BytesIO(base64.b64decode(image_data)))
            else:
                # Assume it's a file path or bytes
                if isinstance(image_input, bytes):
                    image = Image.open(io.BytesIO(image_input))
                else:
                    image = Image.open(image_input)
            
            # Preprocess image
            inputs = self.processor(images=image, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get image embedding
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
                embedding = image_features.cpu().numpy()[0].tolist()
            
            return embedding
            
        except Exception as e:
            print(f"Error encoding image: {e}")
            return await self._mock_embedding()
    
    async def encode_text(self, text: str) -> List[float]:
        """Encode text to CLIP embedding"""
        try:
            if self.model is None:
                return await self._mock_embedding()
            
            # Preprocess text
            inputs = self.processor(text=text, return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get text embedding
            with torch.no_grad():
                text_features = self.model.get_text_features(**inputs)
                embedding = text_features.cpu().numpy()[0].tolist()
            
            return embedding
            
        except Exception as e:
            print(f"Error encoding text: {e}")
            return await self._mock_embedding()
    
    async def compute_similarity(
        self, 
        image_embedding: List[float], 
        text_embedding: List[float]
    ) -> float:
        """Compute cosine similarity between image and text embeddings"""
        try:
            if self.model is None:
                return await self._mock_similarity()
            
            # Convert to numpy arrays
            img_emb = np.array(image_embedding)
            txt_emb = np.array(text_embedding)
            
            # Normalize embeddings
            img_emb = img_emb / np.linalg.norm(img_emb)
            txt_emb = txt_emb / np.linalg.norm(txt_emb)
            
            # Compute cosine similarity
            similarity = np.dot(img_emb, txt_emb)
            
            return float(similarity)
            
        except Exception as e:
            print(f"Error computing similarity: {e}")
            return await self._mock_similarity()
    
    async def compute_image_similarity(
        self, 
        image_embedding1: List[float], 
        image_embedding2: List[float]
    ) -> float:
        """Compute cosine similarity between two image embeddings"""
        try:
            if self.model is None:
                return await self._mock_similarity()
            
            # Convert to numpy arrays
            emb1 = np.array(image_embedding1)
            emb2 = np.array(image_embedding2)
            
            # Normalize embeddings
            emb1 = emb1 / np.linalg.norm(emb1)
            emb2 = emb2 / np.linalg.norm(emb2)
            
            # Compute cosine similarity
            similarity = np.dot(emb1, emb2)
            
            return float(similarity)
            
        except Exception as e:
            print(f"Error computing image similarity: {e}")
            return await self._mock_similarity()
    
    async def find_most_similar(
        self, 
        query_embedding: List[float], 
        candidate_embeddings: List[List[float]]
    ) -> Dict[str, Any]:
        """Find most similar embedding from candidates"""
        try:
            if self.model is None:
                return await self._mock_most_similar()
            
            similarities = []
            for candidate in candidate_embeddings:
                similarity = await self.compute_image_similarity(
                    query_embedding, candidate
                )
                similarities.append(similarity)
            
            # Find best match
            best_idx = np.argmax(similarities)
            best_similarity = similarities[best_idx]
            
            return {
                "best_index": int(best_idx),
                "best_similarity": best_similarity,
                "all_similarities": similarities
            }
            
        except Exception as e:
            print(f"Error finding most similar: {e}")
            return await self._mock_most_similar()
    
    async def _mock_embedding(self) -> List[float]:
        """Mock embedding for development"""
        return [0.1] * 512  # CLIP embeddings are typically 512-dimensional
    
    async def _mock_similarity(self) -> float:
        """Mock similarity for development"""
        return 0.75
    
    async def _mock_most_similar(self) -> Dict[str, Any]:
        """Mock most similar result for development"""
        return {
            "best_index": 0,
            "best_similarity": 0.85,
            "all_similarities": [0.85, 0.72, 0.68, 0.91, 0.63]
        }
