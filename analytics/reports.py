import pandas as pd
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class KPIReportGenerator:
    """Generates Key Performance Indicators from the SQLite database."""
    
    def __init__(self, db_path: str = "database/road_risk.db"):
        self.db_path = Path(db_path)
        
    def get_connection(self):
        return sqlite3.connect(self.db_path)
        
    def generate_kpis(self) -> dict:
        logging.info("Generating KPIs...")
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Total Accidents
            cursor.execute("SELECT COUNT(*) FROM accidents")
            total_accidents = cursor.fetchone()[0]
            
            # Critical Zones (risk_score > 80)
            cursor.execute("SELECT COUNT(*) FROM risk_scores WHERE risk_score > 80")
            critical_zones = cursor.fetchone()[0]
            
            # Average Risk Score
            cursor.execute("SELECT AVG(risk_score) FROM risk_scores")
            avg_risk = cursor.fetchone()[0]
            
            # Most Dangerous Hour
            cursor.execute("SELECT peak_hour, COUNT(*) as count FROM zone_statistics GROUP BY peak_hour ORDER BY count DESC LIMIT 1")
            most_dangerous_hour = cursor.fetchone()[0]
            
            # Fatality Rate
            cursor.execute("SELECT SUM(fatal_count), SUM(accident_count) FROM zone_statistics")
            fatal_count, acc_count = cursor.fetchone()
            fatality_rate = (fatal_count / acc_count) * 100 if acc_count else 0
            
            kpis = {
                "Total Accidents": f"{total_accidents:,}",
                "Critical Zones": f"{critical_zones:,}",
                "Average Risk Score": f"{avg_risk:.1f}",
                "Most Dangerous Hour": f"{int(most_dangerous_hour):02d}:00",
                "Fatality Rate": f"{fatality_rate:.1f}%"
            }
            return kpis
        except Exception as e:
            logging.error(f"Error generating KPIs: {e}")
            return {}
        finally:
            conn.close()

    def generate_top_rankings(self):
        logging.info("Generating Top 10 Rankings...")
        conn = self.get_connection()
        try:
            # Top dangerous zones
            top_zones = pd.read_sql_query("SELECT h3_index, risk_score, explanation FROM risk_scores ORDER BY risk_score DESC LIMIT 10", conn)
            top_zones.to_sql("top_dangerous_zones", conn, if_exists="replace", index=False)
            
            # Top dangerous hours
            top_hours = pd.read_sql_query("SELECT peak_hour as hour, SUM(accident_count) as total_accidents FROM zone_statistics GROUP BY peak_hour ORDER BY total_accidents DESC LIMIT 10", conn)
            top_hours.to_sql("top_dangerous_hours", conn, if_exists="replace", index=False)
            
            logging.info("Top 10 Rankings successfully saved to SQLite.")
        except Exception as e:
            logging.error(f"Error generating rankings: {e}")
        finally:
            conn.close()
