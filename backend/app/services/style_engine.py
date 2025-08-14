from typing import List, Dict, Any, Optional
import numpy as np
import time
import uuid

from app.services.clip_service import CLIPService

class StyleEngine:
    """Style Engine for CLIP embeddings and style match scoring"""
    
    def __init__(self):
        self.clip_service = None
        self.style_cache = {}  # In-memory cache for style embeddings
        self.similarity_threshold = 0.7
    
    async def initialize(self, clip_service: CLIPService):
        """Initialize with CLIP service"""
        self.clip_service = clip_service
    
    async def match_style(
        self,
        frame: bytes,
        segmentation_results: List[Dict[str, Any]],
        style_id: str
    ) -> List[Dict[str, Any]]:
        """Match current frame against reference style"""
        try:
            # Get style embeddings from cache/database
            style_embeddings = await self.get_style_embeddings(style_id)
            if not style_embeddings:
                return [self._create_style_feedback(
                    "No reference style found", 0.0, "low"
                )]
            
            # Encode current frame
            frame_embedding = await self.clip_service.encode_image(frame)
            
            # Calculate similarities with all reference images
            similarities = []
            for ref_embedding in style_embeddings:
                similarity = await self.clip_service.compute_image_similarity(
                    frame_embedding, ref_embedding
                )
                similarities.append(similarity)
            
            # Get best match
            best_similarity = max(similarities) if similarities else 0.0
            avg_similarity = np.mean(similarities) if similarities else 0.0
            
            # Generate feedback based on similarity
            feedback = []
            
            if best_similarity > self.similarity_threshold:
                feedback.append(self._create_style_feedback(
                    f"Excellent style match! This outfit closely resembles your reference style ({best_similarity:.1%} similarity)",
                    best_similarity, "high"
                ))
            elif avg_similarity > 0.5:
                feedback.append(self._create_style_feedback(
                    f"Good style alignment. Your outfit has {avg_similarity:.1%} similarity with your reference style",
                    avg_similarity, "medium"
                ))
            else:
                feedback.append(self._create_style_feedback(
                    f"Consider adjusting your outfit to better match your reference style (current similarity: {avg_similarity:.1%})",
                    avg_similarity, "high"
                ))
            
            # Add specific garment feedback if segmentation is available
            if segmentation_results:
                garment_feedback = await self._analyze_garment_style_match(
                    frame, segmentation_results, style_embeddings
                )
                feedback.extend(garment_feedback)
            
            return feedback
            
        except Exception as e:
            print(f"Error in style matching: {e}")
            return [self._create_style_feedback(
                "Style matching unavailable", 0.0, "low"
            )]
    
    async def get_style_embeddings(self, style_id: str) -> List[List[float]]:
        """Get style embeddings from cache or database"""
        try:
            # Check cache first
            if style_id in self.style_cache:
                return self.style_cache[style_id]
            
            # In production, fetch from database
            # For now, return mock embeddings
            mock_embeddings = [
                [0.1] * 512,  # Mock embedding 1
                [0.2] * 512,  # Mock embedding 2
                [0.15] * 512  # Mock embedding 3
            ]
            
            # Cache the embeddings
            self.style_cache[style_id] = mock_embeddings
            
            return mock_embeddings
            
        except Exception as e:
            print(f"Error getting style embeddings: {e}")
            return []
    
    async def compute_similarity(
        self,
        frame: bytes,
        style_embeddings: List[List[float]]
    ) -> float:
        """Compute similarity between frame and style embeddings"""
        try:
            if not style_embeddings:
                return 0.0
            
            # Encode frame
            frame_embedding = await self.clip_service.encode_image(frame)
            
            # Calculate similarities
            similarities = []
            for style_embedding in style_embeddings:
                similarity = await self.clip_service.compute_image_similarity(
                    frame_embedding, style_embedding
                )
                similarities.append(similarity)
            
            # Return average similarity
            return float(np.mean(similarities)) if similarities else 0.0
            
        except Exception as e:
            print(f"Error computing similarity: {e}")
            return 0.0
    
    async def _analyze_garment_style_match(
        self,
        frame: bytes,
        segmentation_results: List[Dict[str, Any]],
        style_embeddings: List[List[float]]
    ) -> List[Dict[str, Any]]:
        """Analyze individual garment style matching"""
        feedback = []
        
        try:
            for seg_result in segmentation_results:
                garment_class = seg_result["class"]
                
                # Extract garment region (simplified - in production, use actual mask)
                bbox = seg_result["bbox"]
                
                # For now, create mock garment embedding
                garment_embedding = [0.1] * 512  # Mock embedding
                
                # Calculate similarity with style
                similarities = []
                for style_embedding in style_embeddings:
                    similarity = await self.clip_service.compute_image_similarity(
                        garment_embedding, style_embedding
                    )
                    similarities.append(similarity)
                
                avg_similarity = np.mean(similarities) if similarities else 0.0
                
                # Generate garment-specific feedback
                if avg_similarity > 0.8:
                    feedback.append(self._create_style_feedback(
                        f"The {garment_class} perfectly matches your reference style",
                        avg_similarity, "medium"
                    ))
                elif avg_similarity > 0.6:
                    feedback.append(self._create_style_feedback(
                        f"The {garment_class} works well with your reference style",
                        avg_similarity, "low"
                    ))
                else:
                    feedback.append(self._create_style_feedback(
                        f"Consider a different {garment_class} to better match your reference style",
                        avg_similarity, "high"
                    ))
        
        except Exception as e:
            print(f"Error analyzing garment style match: {e}")
        
        return feedback
    
    def _create_style_feedback(
        self,
        message: str,
        confidence: float,
        priority: str
    ) -> Dict[str, Any]:
        """Create standardized style feedback"""
        return {
            "type": "style",
            "message": message,
            "confidence": confidence,
            "priority": priority,
            "actionable": True
        }
    
    async def create_style_profile(
        self,
        image_urls: List[str],
        tags: List[str],
        description: Optional[str] = None
    ) -> str:
        """Create a new style profile"""
        try:
            style_id = f"style_{uuid.uuid4().hex[:8]}"
            
            # Generate embeddings for all images
            embeddings = []
            for url in image_urls:
                embedding = await self.clip_service.encode_image(url)
                embeddings.append(embedding)
            
            # Store in cache (in production, store in database)
            self.style_cache[style_id] = embeddings
            
            # In production, save to database with metadata
            # await self._save_style_to_db(style_id, image_urls, tags, description, embeddings)
            
            return style_id
            
        except Exception as e:
            print(f"Error creating style profile: {e}")
            return f"style_{int(time.time())}"
    
    async def update_style_profile(
        self,
        style_id: str,
        new_image_urls: List[str],
        new_tags: Optional[List[str]] = None
    ) -> bool:
        """Update existing style profile"""
        try:
            # Generate new embeddings
            new_embeddings = []
            for url in new_image_urls:
                embedding = await self.clip_service.encode_image(url)
                new_embeddings.append(embedding)
            
            # Update cache
            if style_id in self.style_cache:
                self.style_cache[style_id].extend(new_embeddings)
            else:
                self.style_cache[style_id] = new_embeddings
            
            # In production, update database
            # await self._update_style_in_db(style_id, new_image_urls, new_tags, new_embeddings)
            
            return True
            
        except Exception as e:
            print(f"Error updating style profile: {e}")
            return False
    
    async def delete_style_profile(self, style_id: str) -> bool:
        """Delete style profile"""
        try:
            # Remove from cache
            if style_id in self.style_cache:
                del self.style_cache[style_id]
            
            # In production, delete from database
            # await self._delete_style_from_db(style_id)
            
            return True
            
        except Exception as e:
            print(f"Error deleting style profile: {e}")
            return False
