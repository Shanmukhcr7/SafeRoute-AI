class WeatherContext:
    """Evaluates weather conditions and generates risk modifiers."""
    
    def __init__(self, rain: bool, fog: bool, snow: bool, temp: float):
        self.rain = rain
        self.fog = fog
        self.snow = snow
        self.temp = temp
        
    def evaluate(self) -> dict:
        modifier = 0.0
        explanations = []
        
        # Rain reduces grip and visibility
        if self.rain:
            modifier += 15.0
            explanations.append("Rain (-30% Visibility, -20% Road Grip)")
            
        # Fog reduces visibility drastically
        if self.fog:
            modifier += 25.0
            explanations.append("Fog (-70% Visibility)")
            
        # Snow/Ice reduces grip drastically
        if self.snow or self.temp < 0:
            modifier += 30.0
            explanations.append("Ice/Snow (-80% Road Grip)")
            
        return {
            "weather_modifier": modifier,
            "weather_explanations": explanations
        }
