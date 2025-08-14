# backend/app/services/ai_orchestrator.py
from typing import Optional, Dict, Any
from app.services.openai_client import analyze_frame_b64

class AIOrchestrator:
    """
    OpenAI-only orchestrator:
    - GENERAL mode: analyze single frame with fashion feedback
    - STYLE mode: includes style_profile (JSON) if provided
    Returns a dict matching AnalysisResult schema: overlays, messages, styleMatch?
    """

    @staticmethod
    def analyze_frame(mode: str, frame_b64: str, season: str = "summer", style_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Delegate to OpenAI client (structured JSON output)
        return analyze_frame_b64(mode, frame_b64, season, style_profile)
