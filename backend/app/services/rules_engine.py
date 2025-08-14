from typing import List, Dict, Any, Optional
import numpy as np

class RulesEngine:
    """Rules and Recommendations engine for proportions and fit logic"""
    
    def __init__(self):
        # Fashion rules and guidelines
        self.proportion_rules = {
            "shirt_length": {
                "ideal_ratio": 0.4,  # Shirt should cover 40% of body height
                "tolerance": 0.1
            },
            "pants_length": {
                "ideal_ratio": 0.6,  # Pants should cover 60% of body height
                "tolerance": 0.1
            },
            "waist_position": {
                "ideal_ratio": 0.5,  # Waist should be at 50% of body height
                "tolerance": 0.05
            }
        }
        
        self.fit_rules = {
            "loose": {
                "shoulder_fit": 0.1,  # 10% extra space
                "chest_fit": 0.15,    # 15% extra space
                "waist_fit": 0.2      # 20% extra space
            },
            "fitted": {
                "shoulder_fit": 0.02,  # 2% extra space
                "chest_fit": 0.05,     # 5% extra space
                "waist_fit": 0.08      # 8% extra space
            },
            "oversized": {
                "shoulder_fit": 0.25,  # 25% extra space
                "chest_fit": 0.3,      # 30% extra space
                "waist_fit": 0.35      # 35% extra space
            }
        }
    
    async def analyze_proportions(
        self,
        detections: List[Dict[str, Any]],
        segmentation_results: List[Dict[str, Any]],
        user_prefs: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Analyze clothing proportions and provide feedback"""
        try:
            feedback = []
            
            # Extract person detection
            person_detection = self._find_person_detection(detections)
            if not person_detection:
                return [self._create_feedback(
                    "general", 
                    "No person detected in the image", 
                    0.5, 
                    "low"
                )]
            
            # Analyze garment proportions
            garment_feedback = await self._analyze_garment_proportions(
                detections, person_detection, user_prefs
            )
            feedback.extend(garment_feedback)
            
            # Analyze fit quality
            fit_feedback = await self._analyze_fit_quality(
                detections, person_detection, user_prefs
            )
            feedback.extend(fit_feedback)
            
            # Analyze overall balance
            balance_feedback = await self._analyze_outfit_balance(
                detections, person_detection, user_prefs
            )
            feedback.extend(balance_feedback)
            
            return feedback
            
        except Exception as e:
            print(f"Error in proportion analysis: {e}")
            return [self._create_feedback(
                "general", 
                "Error analyzing proportions", 
                0.5, 
                "low"
            )]
    
    async def _analyze_garment_proportions(
        self,
        detections: List[Dict[str, Any]],
        person_detection: Dict[str, Any],
        user_prefs: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Analyze individual garment proportions"""
        feedback = []
        
        person_bbox = person_detection["bbox"]
        person_height = person_bbox[3] - person_bbox[1]
        
        for detection in detections:
            if detection["class"] in ["shirt", "pants", "dress"]:
                garment_bbox = detection["bbox"]
                garment_height = garment_bbox[3] - garment_bbox[1]
                garment_ratio = garment_height / person_height
                
                if detection["class"] == "shirt":
                    ideal_ratio = self.proportion_rules["shirt_length"]["ideal_ratio"]
                    tolerance = self.proportion_rules["shirt_length"]["tolerance"]
                    
                    if abs(garment_ratio - ideal_ratio) > tolerance:
                        if garment_ratio > ideal_ratio + tolerance:
                            feedback.append(self._create_feedback(
                                "proportion",
                                "The shirt appears too long for your body proportions",
                                0.8,
                                "medium",
                                True
                            ))
                        else:
                            feedback.append(self._create_feedback(
                                "proportion",
                                "The shirt appears too short for your body proportions",
                                0.8,
                                "medium",
                                True
                            ))
                    else:
                        feedback.append(self._create_feedback(
                            "proportion",
                            "The shirt length is well-proportioned for your body",
                            0.9,
                            "low",
                            False
                        ))
                
                elif detection["class"] == "pants":
                    ideal_ratio = self.proportion_rules["pants_length"]["ideal_ratio"]
                    tolerance = self.proportion_rules["pants_length"]["tolerance"]
                    
                    if abs(garment_ratio - ideal_ratio) > tolerance:
                        if garment_ratio > ideal_ratio + tolerance:
                            feedback.append(self._create_feedback(
                                "proportion",
                                "The pants appear too long for your body proportions",
                                0.8,
                                "medium",
                                True
                            ))
                        else:
                            feedback.append(self._create_feedback(
                                "proportion",
                                "The pants appear too short for your body proportions",
                                0.8,
                                "medium",
                                True
                            ))
                    else:
                        feedback.append(self._create_feedback(
                            "proportion",
                            "The pants length is well-proportioned for your body",
                            0.9,
                            "low",
                            False
                        ))
        
        return feedback
    
    async def _analyze_fit_quality(
        self,
        detections: List[Dict[str, Any]],
        person_detection: Dict[str, Any],
        user_prefs: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Analyze fit quality of garments"""
        feedback = []
        
        # Get user's fit preference
        fit_preference = user_prefs.get("fit_preferences", "fitted") if user_prefs else "fitted"
        
        for detection in detections:
            if detection["class"] in ["shirt", "pants", "dress"]:
                # Analyze fit based on detection confidence and bbox size
                confidence = detection["confidence"]
                
                if confidence > 0.9:
                    feedback.append(self._create_feedback(
                        "fit",
                        f"The {detection['class']} appears to fit well",
                        0.85,
                        "low",
                        False
                    ))
                elif confidence > 0.7:
                    feedback.append(self._create_feedback(
                        "fit",
                        f"The {detection['class']} fit could be improved",
                        0.75,
                        "medium",
                        True
                    ))
                else:
                    feedback.append(self._create_feedback(
                        "fit",
                        f"The {detection['class']} doesn't appear to fit properly",
                        0.65,
                        "high",
                        True
                    ))
        
        return feedback
    
    async def _analyze_outfit_balance(
        self,
        detections: List[Dict[str, Any]],
        person_detection: Dict[str, Any],
        user_prefs: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Analyze overall outfit balance and coordination"""
        feedback = []
        
        # Count different garment types
        garment_types = [det["class"] for det in detections if det["class"] in ["shirt", "pants", "dress", "skirt", "jacket"]]
        
        if len(garment_types) >= 2:
            # Check for basic coordination
            if "shirt" in garment_types and "pants" in garment_types:
                feedback.append(self._create_feedback(
                    "style",
                    "Good basic outfit coordination with shirt and pants",
                    0.8,
                    "low",
                    False
                ))
            elif "dress" in garment_types:
                feedback.append(self._create_feedback(
                    "style",
                    "Dress provides a cohesive, coordinated look",
                    0.85,
                    "low",
                    False
                ))
            
            # Check for layering
            if "jacket" in garment_types:
                feedback.append(self._create_feedback(
                    "style",
                    "Good use of layering with the jacket",
                    0.8,
                    "medium",
                    False
                ))
        else:
            feedback.append(self._create_feedback(
                "style",
                "Consider adding more pieces for a complete outfit",
                0.7,
                "medium",
                True
            ))
        
        return feedback
    
    def _find_person_detection(self, detections: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find person detection in the list"""
        for detection in detections:
            if detection["class"] == "person":
                return detection
        return None
    
    def _create_feedback(
        self,
        feedback_type: str,
        message: str,
        confidence: float,
        priority: str,
        actionable: bool = True
    ) -> Dict[str, Any]:
        """Create standardized feedback object"""
        return {
            "type": feedback_type,
            "message": message,
            "confidence": confidence,
            "priority": priority,
            "actionable": actionable
        }
