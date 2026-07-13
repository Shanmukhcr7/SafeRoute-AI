import math

class ZoneMonitor:
    """Calculates Time To Enter (TTE) for upcoming zones based on telemetry."""
    
    def calculate_tte(self, current_speed_kmh: float, distance_to_zone_m: float) -> float:
        """
        Calculates the seconds remaining before entering a zone.
        Returns float('inf') if vehicle is stationary.
        """
        if current_speed_kmh <= 0:
            return float('inf')
            
        # Convert km/h to m/s
        speed_ms = current_speed_kmh * (1000.0 / 3600.0)
        
        # TTE = Distance / Speed
        tte_seconds = distance_to_zone_m / speed_ms
        return tte_seconds
        
    def evaluate_approach(self, speed: float, distance: float, zone_risk_level: str) -> dict:
        """
        Evaluates the danger of an approach and triggers the base alert level.
        """
        tte = self.calculate_tte(speed, distance)
        
        # Basic logical trigger thresholds
        alert_level = 0
        
        if zone_risk_level == "CRITICAL":
            if tte < 10.0:
                alert_level = 5 # Emergency
            elif tte < 30.0:
                alert_level = 4 # Critical
            else:
                alert_level = 3 # Warning
        elif zone_risk_level == "DANGER":
            if tte < 15.0:
                alert_level = 4
            elif tte < 45.0:
                alert_level = 3
        elif zone_risk_level == "WARNING":
            if tte < 20.0:
                alert_level = 3
            else:
                alert_level = 2 # Caution
                
        return {
            "tte_seconds": tte,
            "distance_m": distance,
            "suggested_level": alert_level
        }
