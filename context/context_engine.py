from .weather import WeatherContext
from .time_context import TimeContext
from .road_context import RoadContext
from .gps import GPSContext
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ContextEngine:
    """Merges all live conditions into a single Context Object."""
    
    def build_context(self, raw_data: dict) -> dict:
        logging.info("Building Live Context Object...")
        
        weather = WeatherContext(
            rain=raw_data.get('rain', False),
            fog=raw_data.get('fog', False),
            snow=raw_data.get('snow', False),
            temp=raw_data.get('temp', 20.0)
        ).evaluate()
        
        time_ctx = TimeContext(
            hour=raw_data.get('hour', 12)
        ).evaluate()
        
        road = RoadContext(
            road_type=raw_data.get('road_type', 'City'),
            is_curve=raw_data.get('is_curve', False)
        ).evaluate()
        
        gps = GPSContext(
            lat=raw_data.get('lat', 0.0),
            lon=raw_data.get('lon', 0.0),
            speed=raw_data.get('speed', 0.0),
            heading=raw_data.get('heading', 0)
        ).evaluate()
        
        # Merge all into Context Object
        context_object = {
            "h3_zone": gps['h3_zone'],
            "speed": raw_data.get('speed', 0.0),
            "modifiers": {
                "weather": weather['weather_modifier'],
                "time": time_ctx['time_modifier'],
                "road": road['road_modifier'],
                "speed": gps['speed_modifier']
            },
            "explanations": weather['weather_explanations'] + time_ctx['time_explanations'] + road['road_explanations'] + gps['gps_explanations'],
            # Raw data passed through for the AI Predictor (Phase 5)
            "raw_features": {
                "is_rain": 1 if raw_data.get('rain') else 0,
                "is_fog": 1 if raw_data.get('fog') else 0,
                "is_snow": 1 if raw_data.get('snow') else 0,
                "is_curve": 1 if raw_data.get('is_curve') else 0,
                "hour": raw_data.get('hour', 12),
                "is_night": 1 if raw_data.get('hour', 12) >= 20 or raw_data.get('hour', 12) <= 5 else 0,
                "is_rush_hour": 1 if raw_data.get('hour', 12) in [7, 8, 9, 17, 18, 19] else 0
            }
        }
        
        return context_object
