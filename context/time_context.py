class TimeContext:
    """Evaluates temporal conditions and generates risk modifiers."""
    
    def __init__(self, hour: int):
        self.hour = hour
        
    def evaluate(self) -> dict:
        modifier = 0.0
        explanations = []
        
        # Night driving reduces visibility and increases fatigue
        if self.hour >= 20 or self.hour <= 5:
            modifier += 10.0
            explanations.append("Night Driving (-40% Visibility, High Fatigue)")
            
        # Rush hour increases density and collisions
        elif self.hour in [7, 8, 9, 17, 18, 19]:
            modifier += 5.0
            explanations.append("Rush Hour (High Traffic Density)")
            
        return {
            "time_modifier": modifier,
            "time_explanations": explanations
        }
