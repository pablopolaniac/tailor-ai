import os
import json
from typing import Optional, Dict, Any
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your_openai_api_key_here"))

def analyze_frame_b64(mode: str, frame_b64: str, season: str = "summer", style_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyzes a single base64 encoded frame using OpenAI's GPT-4o Vision model.
    Returns structured JSON output for fashion feedback and overlay data.
    """
    try:
        # Check if OpenAI API key is set
        api_key = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')
        if api_key == 'your_openai_api_key_here':
            # Return mock response for testing
            print("OpenAI API key not set - returning mock response")
            return {
                "feedback": [
                    {
                        "type": "overall",
                        "message": "This is a mock analysis response. Set your OpenAI API key for real analysis.",
                        "confidence": 0.8,
                        "priority": "medium",
                        "actionable": True
                    },
                    {
                        "type": "style",
                        "message": "Your outfit shows good style coordination. Consider adding accessories for a complete look.",
                        "confidence": 0.75,
                        "priority": "low",
                        "actionable": True
                    }
                ],
                "overlay_data": {
                    "bounding_boxes": [],
                    "keypoints": [],
                    "segmentation_masks": [],
                    "guide_lines": [],
                    "color_analysis": {
                        "skin_tone": "neutral",
                        "dominant_colors": ["blue", "black"],
                        "color_harmony": "good",
                        "color_contrast": "medium",
                        "seasonal_analysis": "autumn"
                    }
                },
                "confidence_score": 0.8
            }

        # Prepare the prompt based on mode
        if mode == "general":
            system_prompt = f"""You are TailorAI, a casual, friendly fashion advisor for users aged 18–35 who care about style and self-expression.  
Your goal: give concise, useful, real-world outfit feedback that feels like advice from a stylish friend — not a fashion textbook.

**Current Season: {season.title()}** - Consider this when making recommendations. Don't suggest heavy layers in summer or light fabrics in winter.

Tone & Style Rules:
- Casual, friendly, and conversational.
- Avoid jargon like "cohesion" or "silhouette" — use everyday language.
- Give honest, constructive tips — not only compliments.
- Keep it actionable but not overly critical.
- Be specific: mention colors, fit, and style choices directly.
- Reference skin tone and undertones when relevant for color advice.
- If something looks great, say why in simple terms.
- **Season-appropriate suggestions only** - consider the current season ({season}) when recommending layers, fabrics, or accessories.

Output Format:
Always return exactly 5 short sections in this order:
1. Top/Shirt: [Max 20 words, 1 useful tip or praise]
2. Bottom/Pants: [Max 20 words, 1 useful tip or praise]
3. Footwear: [Max 20 words, 1 useful tip or praise]
4. Accessories: [Max 20 words, tip or idea — if none present, suggest one]
5. Overall Outfit: [Max 30 words, general vibe + color analysis + improvement idea]

Rules:
- No scores or percentages.
- No repeating points.
- One tip per section.
- Mention undertones, contrast, or color harmony in Overall Outfit if relevant.
- **Season-appropriate recommendations only** - no heavy jackets in summer, no light fabrics in winter.

Output **only** the 5 sections, no additional text or formatting."""
            
            user_prompt = f"Analyze this outfit for {season} and give friendly, actionable feedback."

        else:  # style mode
            style_info = ""
            if style_profile:
                style_info = f"\nReference Style Profile: {json.dumps(style_profile, indent=2)}"
            
            system_prompt = f"""You are TailorAI, a casual, friendly fashion advisor for users aged 18–35 who want their outfit to match a specific style reference or aesthetic.  
Your goal: give short, targeted feedback on how closely the outfit matches the reference, and what to tweak to get closer.

**Current Season: {season.title()}** - Consider this when making recommendations. Don't suggest heavy layers in summer or light fabrics in winter.

Tone & Style Rules:
- Casual, friendly, and conversational.
- Avoid jargon — speak like a stylish friend giving advice.
- Give constructive, actionable feedback — not generic praise.
- Keep each point focused on moving closer to the target style.
- Reference skin tone and undertones when relevant for color advice.
- Be specific about the differences between the current outfit and the reference.
- **Season-appropriate suggestions only** - consider the current season ({season}) when recommending changes.

Output Format:
Always return exactly 5 short sections in this order:
1. Top/Shirt: [Max 20 words, tweak or praise relevant to matching style]
2. Bottom/Pants: [Max 20 words, tweak or praise relevant to matching style]
3. Footwear: [Max 20 words, tweak or praise relevant to matching style]
4. Accessories: [Max 20 words, suggest accessories that match style — or praise existing ones]
5. Overall Outfit: [Max 30 words, quick verdict on match + 1 improvement tip for color/fabric/vibe]

Rules:
- No scores or percentages.
- No repeating points.
- One tip per section.
- If major style gaps exist, highlight them simply (e.g., "needs softer fabrics").
- **Season-appropriate recommendations only** - no heavy jackets in summer, no light fabrics in winter.

Output **only** the 5 sections, no additional text or formatting."""
            
            user_prompt = f"Compare this outfit to the reference style for {season} and give targeted feedback.{style_info}"
        
        try:
            # Call OpenAI Vision API with optimized settings
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{frame_b64}",
                                    "detail": "low" # Use low detail for faster processing
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1200,  # Increased for detailed JSON
                temperature=0.25,  # Balanced for focused but varied responses
                top_p=0.9,
                timeout=20  # Increased timeout for complex analysis
            )
            
            # Parse the response
            raw_response_content = response.choices[0].message.content.strip()
            
            # Convert the simple text response to frontend format
            return convert_simple_response_to_frontend_format(raw_response_content, mode)
        
        except Exception as e:
            print(f"OpenAI API error: {e}")
            
            # Check if it's a quota error
            if "quota" in str(e).lower() or "429" in str(e):
                error_message = "OpenAI quota exceeded. Please check your billing or try again later."
            else:
                error_message = "Analysis service temporarily unavailable. Please try again later."
            
            return {
                "feedback": [
                    {
                        "type": "overall",
                        "message": error_message,
                        "confidence": 0.3,
                        "priority": "medium",
                        "actionable": True
                    }
                ],
                "overlay_data": {
                    "bounding_boxes": [],
                    "keypoints": [],
                    "segmentation_masks": [],
                    "guide_lines": [],
                    "color_analysis": {
                        "skin_tone": "unknown",
                        "dominant_colors": [],
                        "color_harmony": "fair",
                        "color_contrast": "medium",
                        "seasonal_analysis": "unknown"
                    }
                },
                "confidence_score": 0.3
            }

    except Exception as e:
        print(f"General error: {e}")
        return {
            "feedback": [
                {
                    "type": "overall",
                    "message": "Analysis failed. Please try again.",
                    "confidence": 0.3,
                    "priority": "medium",
                    "actionable": True
                }
            ],
            "overlay_data": {
                "bounding_boxes": [],
                "keypoints": [],
                "segmentation_masks": [],
                "guide_lines": [],
                "color_analysis": {
                    "skin_tone": "unknown",
                    "dominant_colors": [],
                    "color_harmony": "fair",
                    "color_contrast": "medium",
                    "seasonal_analysis": "unknown"
                }
            },
            "confidence_score": 0.3
        }

def convert_simple_response_to_frontend_format(response_text: str, mode: str) -> Dict[str, Any]:
    """
    Convert the simple 5-section text response to the frontend-compatible format
    """
    feedback = []
    
    # Split the response into lines and parse each section
    lines = response_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Parse each section based on the format "1. Top/Shirt: [content]"
        if line.startswith('1.') or line.startswith('Top/Shirt:'):
            content = extract_content_from_line(line)
            if content:
                feedback.append({
                    "type": "top",
                    "message": content,
                    "confidence": 0.8,
                    "priority": "medium",
                    "actionable": True
                })
        elif line.startswith('2.') or line.startswith('Bottom/Pants:'):
            content = extract_content_from_line(line)
            if content:
                feedback.append({
                    "type": "bottom",
                    "message": content,
                    "confidence": 0.8,
                    "priority": "medium",
                    "actionable": True
                })
        elif line.startswith('3.') or line.startswith('Footwear:'):
            content = extract_content_from_line(line)
            if content:
                feedback.append({
                    "type": "footwear",
                    "message": content,
                    "confidence": 0.8,
                    "priority": "medium",
                    "actionable": True
                })
        elif line.startswith('4.') or line.startswith('Accessories:'):
            content = extract_content_from_line(line)
            if content:
                feedback.append({
                    "type": "accessories",
                    "message": content,
                    "confidence": 0.8,
                    "priority": "low",
                    "actionable": True
                })
        elif line.startswith('5.') or line.startswith('Overall Outfit:'):
            content = extract_content_from_line(line)
            if content:
                feedback.append({
                    "type": "overall",
                    "message": content,
                    "confidence": 0.8,
                    "priority": "medium",
                    "actionable": False
                })
    
    # If no feedback was parsed, create a fallback
    if not feedback:
        feedback = [{
            "type": "overall",
            "message": "Analysis completed. Check the response for detailed feedback.",
            "confidence": 0.8,
            "priority": "medium",
            "actionable": False
        }]
    
    return {
        "feedback": feedback,
        "overlay_data": {
            "bounding_boxes": [],
            "keypoints": [],
            "segmentation_masks": [],
            "guide_lines": [],
            "color_analysis": {
                "skin_tone": "unknown",
                "dominant_colors": [],
                "color_harmony": "fair",
                "color_contrast": "medium",
                "seasonal_analysis": "unknown"
            }
        },
        "confidence_score": 0.8
    }

def extract_content_from_line(line: str) -> str:
    """
    Extract the content from a line like "1. Top/Shirt: [content]" or "Top/Shirt: [content]"
    """
    # Remove numbering and section headers
    if ':' in line:
        content = line.split(':', 1)[1].strip()
        # Remove brackets if present
        if content.startswith('[') and content.endswith(']'):
            content = content[1:-1].strip()
        return content
    return line.strip()
