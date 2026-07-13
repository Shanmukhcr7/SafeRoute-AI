import h3

class GPSContext:
    """Handles vehicle positioning and maps GPS to H3 spatial zones."""
    
    def __init__(self, lat: float, lon: float, speed: float, heading: int):
        self.lat = lat
        self.lon = lon
        self.speed = speed
        self.heading = heading
        
    def evaluate(self) -> dict:
        # Determine current H3 zone
        zone = h3.latlng_to_cell(self.lat, self.lon, 8)
        
        # Calculate speed modifier
        # Assume >80 km/h is high speed, increasing risk multiplier
        speed_modifier = 0.0
        explanations = []
        
        if self.speed > 80:
            speed_modifier = (self.speed - 80) * 0.5  # Add 0.5 risk for every km/h over 80
            explanations.append(f"High Speed ({self.speed} km/h) - Increased Braking Distance")
            
        return {
            "h3_zone": zone,
            "speed_modifier": speed_modifier,
            "gps_explanations": explanations
        }
