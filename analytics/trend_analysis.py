import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class TrendAnalyzer:
    """Calculates comparative trends and correlation intelligence."""
    
    def __init__(self, processed_data_path: str = "data/processed/processed_features.csv"):
        self.data_path = Path(processed_data_path)
        
    def analyze_trends(self) -> list:
        logging.info("Analyzing trends...")
        try:
            df = pd.read_csv(self.data_path)
            trends = []
            
            # Example 1: Night vs Day Severity
            day_severity = df[df['is_night'] == 0]['fatalities'].mean()
            night_severity = df[df['is_night'] == 1]['fatalities'].mean()
            if day_severity > 0:
                pct_increase = ((night_severity - day_severity) / day_severity) * 100
                trends.append({"condition": "Night", "metric": "severity increase", "value": f"↑ {pct_increase:.0f}%"})
            
            # Example 2: Rain Fatality Increase
            # Assume we have bad_weather flag or is_rain flag
            if 'is_rain' in df.columns:
                clear_fatality = df[df['is_rain'] == 0]['fatalities'].mean()
                rain_fatality = df[df['is_rain'] == 1]['fatalities'].mean()
                if clear_fatality > 0:
                    rain_inc = ((rain_fatality - clear_fatality) / clear_fatality) * 100
                    trends.append({"condition": "Rain", "metric": "fatality increase", "value": f"↑ {rain_inc:.0f}%"})
            
            return trends
        except Exception as e:
            logging.error(f"Error calculating trends: {e}")
            return []

    def get_correlations(self) -> list:
        logging.info("Extracting correlation intelligence...")
        try:
            df = pd.read_csv(self.data_path)
            correlations = []
            
            # Night <-> Fatality
            if 'is_night' in df.columns and 'fatalities' in df.columns:
                corr = df['is_night'].corr(df['fatalities'])
                strength = "Strong" if abs(corr) > 0.7 else "Moderate" if abs(corr) > 0.3 else "Weak"
                correlations.append({"relation": "Night ↔ Fatality", "strength": strength, "value": f"{corr:.2f}"})
                
            # Rain <-> Fatality
            if 'is_rain' in df.columns and 'fatalities' in df.columns:
                corr = df['is_rain'].corr(df['fatalities'])
                strength = "Strong" if abs(corr) > 0.7 else "Moderate" if abs(corr) > 0.3 else "Weak"
                correlations.append({"relation": "Rain ↔ Fatality", "strength": strength, "value": f"{corr:.2f}"})
                
            return correlations
        except Exception as e:
            logging.error(f"Error getting correlations: {e}")
            return []
