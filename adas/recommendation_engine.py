class ADASRecommendationEngine:
    """Generates intelligent driver instructions based on current context and alerts."""
    
    def generate_instruction(self, alert_level: int, weather_ctx: dict, road_ctx: dict) -> list:
        instructions = []
        
        if alert_level >= 4:
            instructions.append("Reduce Speed Immediately")
            instructions.append("Increase Following Distance to 4 seconds")
        elif alert_level == 3:
            instructions.append("Prepare to slow down")
            
        if weather_ctx.get('rain', False) or weather_ctx.get('fog', False):
            instructions.append("Turn On Fog Lights")
            instructions.append("Avoid Overtaking")
            
        if road_ctx.get('is_curve', False):
            instructions.append("Do not brake sharply in curve")
            
        if not instructions:
            instructions.append("Maintain current safe driving")
            
        return list(set(instructions)) # Remove duplicates
