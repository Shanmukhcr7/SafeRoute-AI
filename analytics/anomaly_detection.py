import pandas as pd
from sklearn.ensemble import IsolationForest
import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class AnomalyDetector:
    """Uses Machine Learning to find unusual accident clusters."""
    
    def __init__(self, db_path: str = "database/road_risk.db"):
        self.db_path = Path(db_path)
        
    def detect_anomalies(self):
        logging.info("Detecting anomalies using Isolation Forest...")
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT * FROM zone_statistics", conn)
            
            if df.empty:
                return []
                
            features = ['accident_count', 'fatal_count', 'rain_percentage', 'night_percentage']
            # Fill NaNs if any
            X = df[features].fillna(0)
            
            # Use Isolation Forest
            model = IsolationForest(contamination=0.01, random_state=42)
            df['anomaly'] = model.fit_predict(X)
            
            # Extract only anomalous zones (model output is -1 for anomalies, 1 for normal)
            anomalies = df[df['anomaly'] == -1].copy()
            
            results = []
            for _, row in anomalies.head(5).iterrows():
                results.append({
                    "h3_index": row['h3_index'],
                    "description": f"⚠ Unusual Accident Cluster Detected (High density or specific weather anomaly)",
                    "severity_mean": row['severity_mean']
                })
            
            return results
        except Exception as e:
            logging.error(f"Error in anomaly detection: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()
