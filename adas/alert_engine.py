import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class AlertEngine:
    """Evaluates multiple inputs to generate a Priority Level Alert."""
    
    def __init__(self):
        self.levels = {
            1: ("🟢", "Information", "Information only."),
            2: ("🟡", "Caution", "Be prepared to react."),
            3: ("🟠", "Warning", "Action recommended soon."),
            4: ("🔴", "Critical", "Immediate action required!"),
            5: ("⚫", "Emergency", "Extreme danger! Stop or evade!")
        }
        
    def generate_alert(self, context: dict, tte_data: dict, driver_profile: str) -> dict:
        """
        Calculates final alert level based on TTE, Weather, and Driver Profile.
        """
        base_level = tte_data.get('suggested_level', 0)
        if base_level == 0:
            return None
            
        # Context Modifiers
        # If it's raining/foggy, escalate the alert by 1 level if we are close
        if context.get('weather_modifier', 0) > 10 and tte_data['tte_seconds'] < 30:
            base_level = min(5, base_level + 1)
            
        # Driver Profile Modifiers
        # Aggressive drivers need earlier/louder warnings to compensate for speed
        if driver_profile == "AGGRESSIVE" and tte_data['tte_seconds'] < 20:
            base_level = min(5, base_level + 1)
            
        emoji, title, desc = self.levels[base_level]
        
        alert_obj = {
            "level": base_level,
            "emoji": emoji,
            "title": title,
            "description": desc,
            "tte": tte_data['tte_seconds']
        }
        
        return alert_obj
