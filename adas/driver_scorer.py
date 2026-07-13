class DriverScorer:
    """Calculates a dynamic safety score for the driver."""
    
    def __init__(self, initial_score: float = 100.0):
        self.score = initial_score
        
    def update_score(self, speed: float, speed_limit: float, zone_risk_level: str, is_raining: bool) -> float:
        """
        Deducts points for unsafe behavior or slowly recovers points for safe behavior.
        """
        penalty = 0.0
        
        # Speeding penalty
        if speed > speed_limit + 10:
            penalty += (speed - speed_limit) * 0.1
            
        # Dangerous zone speeding penalty
        if zone_risk_level in ["DANGER", "CRITICAL"] and speed > 50:
            penalty += 2.0
            
        # Weather ignoring penalty
        if is_raining and speed > 80:
            penalty += 1.5
            
        if penalty > 0:
            self.score = max(0.0, self.score - penalty)
        else:
            # Safe driving recovery
            self.score = min(100.0, self.score + 0.1)
            
        return self.score
