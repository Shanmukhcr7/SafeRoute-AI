class RoadContext:
    """Evaluates road-specific conditions and generates risk modifiers."""
    
    def __init__(self, road_type: str, is_curve: bool):
        self.road_type = road_type
        self.is_curve = is_curve
        
    def evaluate(self) -> dict:
        modifier = 0.0
        explanations = []
        
        # Curve
        if self.is_curve:
            modifier += 10.0
            explanations.append("Sharp Curve (Reduced Control, Blind Spots)")
            
        # Highway vs Rural
        if self.road_type == "Highway":
            modifier += 5.0 # Higher speed environment
        elif self.road_type == "Rural":
            modifier += 10.0 # Poorer lighting, single lane
            explanations.append("Rural Road (High Risk of Head-On Collision)")
            
        return {
            "road_modifier": modifier,
            "road_explanations": explanations
        }
