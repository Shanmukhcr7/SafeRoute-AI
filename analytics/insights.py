import pandas as pd
import logging
from pathlib import Path
import sqlite3

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class InsightGenerator:
    """Generates text-based insights based on statistical rules."""
    
    def __init__(self, db_path: str = "database/road_risk.db"):
        self.db_path = Path(db_path)
        
    def generate_insights(self):
        logging.info("Generating automatic AI insights...")
        try:
            conn = sqlite3.connect(self.db_path)
            # Find the most dangerous zone
            top_zone = pd.read_sql_query("SELECT * FROM zone_statistics ORDER BY accident_count DESC LIMIT 1", conn)
            
            insights = []
            if not top_zone.empty:
                zone = top_zone.iloc[0]
                factors = []
                if zone['rain_percentage'] > 30:
                    factors.append("Wet Surface")
                if zone['night_percentage'] > 40:
                    factors.append("Poor Lighting")
                if zone['curve_percentage'] > 30:
                    factors.append("Curved Roads")
                
                insight_text = (
                    f"This region ({zone['h3_index']}) experiences significantly "
                    f"higher accident rates during evening/night hours.\n"
                    f"Primary contributing factors:\n"
                )
                for f in factors:
                    insight_text += f"• {f}\n"
                    
                insight_text += "\nSuggested Action: Increase Warning Signage"
                
                insights.append({
                    "title": "High Risk Zone Alert",
                    "text": insight_text
                })
            
            return insights
        except Exception as e:
            logging.error(f"Error generating insights: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()
