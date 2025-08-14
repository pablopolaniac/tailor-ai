import openai
import base64
import json
from typing import List, Dict, Any, Optional
from PIL import Image
import io

from app.core.config import settings

class GPTService:
    """GPT-4o Vision service for high-level fashion analysis"""
    
    def __init__(self):
        self.client = None
        self.model = "gpt-4o"
    
    async def load_model(self):
        """Initialize OpenAI client"""
        try:
            print("Initializing GPT-4o service...")
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            print("GPT-4o service initialized successfully")
        except Exception as e:
            print(f"Error initializing GPT-4o service: {e}")
            self.client = None
    
    async def analyze_fashion(
        self,
        frame: bytes,
        detections: List[Dict[str, Any]],
        segmentation_results: List[Dict[str, Any]],
        user_prefs: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Analyze fashion using GPT-4o Vision"""
        try:
            if self.client is None:
                return await self._mock_fashion_analysis()
            
            # Convert frame to base64
            frame_b64 = base64.b64encode(frame).decode('utf-8')
            
            # Prepare context from detections
            context = self._prepare_detection_context(detections, segmentation_results)
            
            # Prepare user preferences context
            prefs_context = self._prepare_preferences_context(user_prefs)
            
            # Create system prompt
            system_prompt = self._create_system_prompt()
            
            # Create user message
            user_message = self._create_user_message(context, prefs_context)
            
            # Call GPT-4o Vision
            response = await self._call_gpt_vision(
                frame_b64, system_prompt, user_message
            )
            
            # Parse response
            feedback = self._parse_gpt_response(response)
            
            return feedback
            
        except Exception as e:
            print(f"Error in GPT fashion analysis: {e}")
            return await self._mock_fashion_analysis()
    
    def _prepare_detection_context(
        self, 
        detections: List[Dict[str, Any]], 
        segmentation_results: List[Dict[str, Any]]
    ) -> str:
        """Prepare context from object detections"""
        context_parts = []
        
        # Add detected objects
        if detections:
            objects = []
            for det in detections:
                obj_info = f"{det['class']} (confidence: {det['confidence']:.2f})"
                objects.append(obj_info)
            context_parts.append(f"Detected objects: {', '.join(objects)}")
        
        # Add segmentation info
        if segmentation_results:
            segments = []
            for seg in segmentation_results:
                segments.append(f"{seg['class']} with mask")
            context_parts.append(f"Segmented garments: {', '.join(segments)}")
        
        return "; ".join(context_parts) if context_parts else "No objects detected"
    
    def _prepare_preferences_context(self, user_prefs: Optional[Dict[str, Any]]) -> str:
        """Prepare context from user preferences"""
        if not user_prefs:
            return "No specific user preferences provided"
        
        prefs_parts = []
        
        if user_prefs.get("style_preferences"):
            prefs_parts.append(f"Style preferences: {', '.join(user_prefs['style_preferences'])}")
        
        if user_prefs.get("color_preferences"):
            prefs_parts.append(f"Color preferences: {', '.join(user_prefs['color_preferences'])}")
        
        if user_prefs.get("fit_preferences"):
            prefs_parts.append(f"Fit preference: {user_prefs['fit_preferences']}")
        
        if user_prefs.get("occasion"):
            prefs_parts.append(f"Occasion: {user_prefs['occasion']}")
        
        if user_prefs.get("body_type"):
            prefs_parts.append(f"Body type: {user_prefs['body_type']}")
        
        return "; ".join(prefs_parts) if prefs_parts else "No specific preferences"
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for fashion analysis"""
        return """You are a professional fashion stylist and image analyst. Your task is to analyze fashion images and provide constructive, actionable feedback.

Focus on:
1. **Proportions**: How well the clothing fits the person's body type
2. **Color Harmony**: How well colors work together and with skin tone
3. **Style Coherence**: How well the outfit works as a whole
4. **Fit Quality**: Whether the clothing fits properly
5. **Occasion Appropriateness**: Whether the outfit is suitable for the intended occasion

Provide feedback in this JSON format:
{
  "feedback": [
    {
      "type": "proportion|color|style|fit|general",
      "message": "Clear, actionable feedback message",
      "confidence": 0.85,
      "priority": "high|medium|low",
      "actionable": true
    }
  ]
}

Be constructive, specific, and helpful. Focus on actionable improvements."""
    
    def _create_user_message(self, detection_context: str, prefs_context: str) -> str:
        """Create user message for GPT analysis"""
        return f"""Please analyze this fashion image and provide feedback.

Context:
- {detection_context}
- {prefs_context}

Analyze the outfit and provide feedback in the specified JSON format."""
    
    async def _call_gpt_vision(
        self, 
        image_b64: str, 
        system_prompt: str, 
        user_message: str
    ) -> str:
        """Call GPT-4o Vision API"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_message},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error calling GPT-4o Vision: {e}")
            raise
    
    def _parse_gpt_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse GPT response into feedback format"""
        try:
            # Try to extract JSON from response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response and "}" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
            else:
                # Fallback to mock response
                return self._create_mock_feedback()
            
            # Parse JSON
            data = json.loads(json_str)
            
            if "feedback" in data and isinstance(data["feedback"], list):
                return data["feedback"]
            else:
                return self._create_mock_feedback()
                
        except Exception as e:
            print(f"Error parsing GPT response: {e}")
            return self._create_mock_feedback()
    
    async def _mock_fashion_analysis(self) -> List[Dict[str, Any]]:
        """Mock fashion analysis for development"""
        return self._create_mock_feedback()
    
    def _create_mock_feedback(self) -> List[Dict[str, Any]]:
        """Create mock feedback for development"""
        return [
            {
                "type": "proportion",
                "message": "The shirt fits well with your body proportions. The shoulder seams align properly with your shoulders.",
                "confidence": 0.88,
                "priority": "medium",
                "actionable": True
            },
            {
                "type": "color",
                "message": "The blue tones in your outfit complement your skin tone nicely. Consider adding a contrasting accessory for more visual interest.",
                "confidence": 0.82,
                "priority": "low",
                "actionable": True
            },
            {
                "type": "style",
                "message": "This is a well-coordinated casual outfit. The combination of shirt and pants creates a balanced, relaxed look.",
                "confidence": 0.90,
                "priority": "medium",
                "actionable": False
            },
            {
                "type": "fit",
                "message": "The pants could be slightly more fitted around the waist for a more polished appearance.",
                "confidence": 0.75,
                "priority": "high",
                "actionable": True
            }
        ]
