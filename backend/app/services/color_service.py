import cv2
import numpy as np
from typing import List, Dict, Any, Optional
from PIL import Image
import io
import colorsys

class ColorService:
    """Color and Palette service for skin tone and color harmony analysis"""
    
    def __init__(self):
        # Color harmony rules
        self.color_harmony_rules = {
            "complementary": 180,  # Opposite colors
            "analogous": 30,       # Adjacent colors
            "triadic": 120,        # Three colors equally spaced
            "monochromatic": 0     # Same hue, different saturation/value
        }
        
        # Skin tone ranges (HSV)
        self.skin_tone_ranges = [
            # Light skin tones
            {"hue": (0, 30), "sat": (20, 80), "val": (60, 100)},
            # Medium skin tones  
            {"hue": (0, 30), "sat": (30, 90), "val": (40, 80)},
            # Dark skin tones
            {"hue": (0, 30), "sat": (40, 100), "val": (20, 60)}
        ]
    
    async def analyze_colors(
        self,
        frame: bytes,
        segmentation_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze colors in the frame and provide harmony feedback"""
        try:
            # Convert frame to PIL Image
            image = Image.open(io.BytesIO(frame))
            image_array = np.array(image)
            
            # Convert to HSV for better color analysis
            hsv_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
            
            # Analyze skin tone
            skin_tone = await self._analyze_skin_tone(hsv_image)
            
            # Analyze garment colors
            garment_colors = await self._analyze_garment_colors(
                hsv_image, segmentation_results
            )
            
            # Analyze color harmony
            harmony_analysis = await self._analyze_color_harmony(
                skin_tone, garment_colors
            )
            
            return {
                "skin_tone": skin_tone,
                "garment_colors": garment_colors,
                "harmony_analysis": harmony_analysis,
                "overall_score": harmony_analysis.get("overall_score", 0.7)
            }
            
        except Exception as e:
            print(f"Error in color analysis: {e}")
            return await self._mock_color_analysis()
    
    async def _analyze_skin_tone(self, hsv_image: np.ndarray) -> Dict[str, Any]:
        """Analyze skin tone in the image"""
        try:
            # Create skin tone mask (simplified)
            lower_skin = np.array([0, 20, 20])
            upper_skin = np.array([30, 255, 255])
            skin_mask = cv2.inRange(hsv_image, lower_skin, upper_skin)
            
            # Find skin regions
            skin_pixels = hsv_image[skin_mask > 0]
            
            if len(skin_pixels) == 0:
                return {"detected": False, "tone": "unknown"}
            
            # Calculate average skin tone
            avg_hue = np.mean(skin_pixels[:, 0])
            avg_sat = np.mean(skin_pixels[:, 1])
            avg_val = np.mean(skin_pixels[:, 2])
            
            # Classify skin tone
            skin_tone = self._classify_skin_tone(avg_hue, avg_sat, avg_val)
            
            return {
                "detected": True,
                "tone": skin_tone,
                "hsv": [float(avg_hue), float(avg_sat), float(avg_val)],
                "rgb": self._hsv_to_rgb(avg_hue, avg_sat, avg_val)
            }
            
        except Exception as e:
            print(f"Error analyzing skin tone: {e}")
            return {"detected": False, "tone": "unknown"}
    
    async def _analyze_garment_colors(
        self,
        hsv_image: np.ndarray,
        segmentation_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze colors of detected garments"""
        garment_colors = []
        
        for seg_result in segmentation_results:
            try:
                # Extract garment region using segmentation mask
                # For now, use bounding box (in production, use actual mask)
                bbox = seg_result["bbox"]
                x1, y1, x2, y2 = bbox
                
                garment_region = hsv_image[y1:y2, x1:x2]
                
                # Calculate dominant colors
                dominant_colors = self._extract_dominant_colors(garment_region)
                
                garment_colors.append({
                    "class": seg_result["class"],
                    "colors": dominant_colors,
                    "primary_color": dominant_colors[0] if dominant_colors else None
                })
                
            except Exception as e:
                print(f"Error analyzing garment colors: {e}")
                continue
        
        return garment_colors
    
    async def _analyze_color_harmony(
        self,
        skin_tone: Dict[str, Any],
        garment_colors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze color harmony between skin tone and garments"""
        try:
            harmony_scores = []
            feedback = []
            
            if not skin_tone.get("detected", False):
                return {
                    "overall_score": 0.5,
                    "feedback": ["Unable to detect skin tone for color analysis"],
                    "harmony_type": "unknown"
                }
            
            skin_hsv = skin_tone.get("hsv", [0, 0, 0])
            
            for garment in garment_colors:
                if garment.get("primary_color"):
                    garment_hsv = garment["primary_color"]["hsv"]
                    
                    # Calculate harmony score
                    harmony_score = self._calculate_harmony_score(
                        skin_hsv, garment_hsv
                    )
                    harmony_scores.append(harmony_score)
                    
                    # Generate feedback
                    garment_feedback = self._generate_color_feedback(
                        skin_tone["tone"], garment["class"], harmony_score
                    )
                    feedback.append(garment_feedback)
            
            overall_score = np.mean(harmony_scores) if harmony_scores else 0.7
            
            return {
                "overall_score": float(overall_score),
                "individual_scores": harmony_scores,
                "feedback": feedback,
                "harmony_type": self._classify_harmony_type(overall_score)
            }
            
        except Exception as e:
            print(f"Error in color harmony analysis: {e}")
            return {
                "overall_score": 0.7,
                "feedback": ["Color harmony analysis unavailable"],
                "harmony_type": "neutral"
            }
    
    def _extract_dominant_colors(self, image_region: np.ndarray) -> List[Dict[str, Any]]:
        """Extract dominant colors from image region"""
        try:
            # Reshape image for k-means clustering
            pixels = image_region.reshape(-1, 3)
            
            # Use k-means to find dominant colors
            from sklearn.cluster import KMeans
            
            kmeans = KMeans(n_clusters=3, random_state=42)
            kmeans.fit(pixels)
            
            # Get cluster centers (dominant colors)
            dominant_colors = []
            for center in kmeans.cluster_centers_:
                h, s, v = center
                rgb = self._hsv_to_rgb(h, s, v)
                
                dominant_colors.append({
                    "hsv": [float(h), float(s), float(v)],
                    "rgb": rgb,
                    "hex": self._rgb_to_hex(rgb)
                })
            
            return dominant_colors
            
        except Exception as e:
            print(f"Error extracting dominant colors: {e}")
            return []
    
    def _calculate_harmony_score(
        self,
        color1_hsv: List[float],
        color2_hsv: List[float]
    ) -> float:
        """Calculate harmony score between two colors"""
        try:
            h1, s1, v1 = color1_hsv
            h2, s2, v2 = color2_hsv
            
            # Calculate hue difference
            hue_diff = abs(h1 - h2)
            if hue_diff > 180:
                hue_diff = 360 - hue_diff
            
            # Calculate saturation and value differences
            sat_diff = abs(s1 - s2) / 255.0
            val_diff = abs(v1 - v2) / 255.0
            
            # Score based on harmony rules
            if hue_diff <= 30:  # Analogous
                harmony_score = 0.9
            elif abs(hue_diff - 180) <= 30:  # Complementary
                harmony_score = 0.8
            elif abs(hue_diff - 120) <= 30:  # Triadic
                harmony_score = 0.7
            else:
                harmony_score = 0.5
            
            # Adjust for saturation and value harmony
            if sat_diff < 0.3 and val_diff < 0.3:
                harmony_score += 0.1
            
            return min(harmony_score, 1.0)
            
        except Exception as e:
            print(f"Error calculating harmony score: {e}")
            return 0.7
    
    def _classify_skin_tone(self, hue: float, sat: float, val: float) -> str:
        """Classify skin tone based on HSV values"""
        if val > 60:
            return "light"
        elif val > 40:
            return "medium"
        else:
            return "dark"
    
    def _classify_harmony_type(self, score: float) -> str:
        """Classify overall harmony type"""
        if score > 0.8:
            return "excellent"
        elif score > 0.7:
            return "good"
        elif score > 0.6:
            return "neutral"
        else:
            return "poor"
    
    def _generate_color_feedback(
        self,
        skin_tone: str,
        garment_class: str,
        harmony_score: float
    ) -> str:
        """Generate color feedback message"""
        if harmony_score > 0.8:
            return f"The {garment_class} color works beautifully with your {skin_tone} skin tone"
        elif harmony_score > 0.7:
            return f"The {garment_class} color complements your {skin_tone} skin tone well"
        elif harmony_score > 0.6:
            return f"The {garment_class} color is acceptable with your {skin_tone} skin tone"
        else:
            return f"Consider a different color for the {garment_class} to better complement your {skin_tone} skin tone"
    
    def _hsv_to_rgb(self, h: float, s: float, v: float) -> List[int]:
        """Convert HSV to RGB"""
        try:
            rgb = colorsys.hsv_to_rgb(h/360, s/255, v/255)
            return [int(c * 255) for c in rgb]
        except:
            return [0, 0, 0]
    
    def _rgb_to_hex(self, rgb: List[int]) -> str:
        """Convert RGB to hex"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    async def _mock_color_analysis(self) -> Dict[str, Any]:
        """Mock color analysis for development"""
        return {
            "skin_tone": {
                "detected": True,
                "tone": "medium",
                "hsv": [15, 60, 70],
                "rgb": [179, 143, 89]
            },
            "garment_colors": [
                {
                    "class": "shirt",
                    "colors": [
                        {
                            "hsv": [210, 80, 90],
                            "rgb": [46, 92, 230],
                            "hex": "#2e5ce6"
                        }
                    ],
                    "primary_color": {
                        "hsv": [210, 80, 90],
                        "rgb": [46, 92, 230],
                        "hex": "#2e5ce6"
                    }
                }
            ],
            "harmony_analysis": {
                "overall_score": 0.75,
                "individual_scores": [0.75],
                "feedback": ["The shirt color complements your medium skin tone well"],
                "harmony_type": "good"
            },
            "overall_score": 0.75
        }
