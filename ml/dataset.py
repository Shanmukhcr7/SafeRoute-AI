import pandas as pd
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class MLDatasetBuilder:
    """Prepares the ML-ready dataset for Severity Prediction."""
    
    def __init__(self, db_path: str = "database/road_risk.db"):
        self.db_path = Path(db_path)
        
    def build_dataset(self) -> pd.DataFrame:
        logging.info("Building ML Dataset from SQLite...")
        conn = sqlite3.connect(self.db_path)
        
        try:
            # We need the original features from processed_accidents (atm, surf, lum, plan, hour, etc.)
            # and the target from the users table (grav). Since grav is per user, we will predict
            # the maximum severity of an accident.
            
            # Fetch processed accidents
            accidents = pd.read_sql_query("SELECT * FROM processed_accidents", conn)
            
            # Fetch max severity per accident
            # Assuming 'users' table has Num_Acc and severity (grav)
            # grav: 1=Uninjured, 2=Fatal, 3=Hospitalized, 4=Minor
            # We map it so 0=Safe, 1=Minor, 2=Hospitalized, 3=Fatal for standard ordinal ML
            
            # Since the users table is populated from raw, let's load raw users to ensure accuracy
            raw_users = pd.read_csv("data/raw/users.csv", encoding='latin-1', low_memory=False)
            
            # Map grav: 1->0 (Uninjured), 4->1 (Minor), 3->2 (Hospitalized), 2->3 (Fatal)
            grav_map = {1: 0, 4: 1, 3: 2, 2: 3}
            raw_users['severity'] = raw_users['grav'].map(grav_map)
            
            # Get max severity per accident
            accident_severity = raw_users.groupby('Num_Acc')['severity'].max().reset_index()
            
            # Merge
            df = pd.merge(accidents, accident_severity, on='Num_Acc', how='inner')
            
            # Select relevant features for the model
            # Environmental: atm, lum, surf
            # Road: plan, prof, agg, int
            # Temporal: hour, is_night, is_rush_hour, is_weekend
            
            features = [
                'atm', 'lum', 'surf', 'plan', 'prof', 'agg', 'int',
                'hour', 'is_night', 'is_rush_hour', 'is_rain', 'is_snow', 
                'is_fog', 'is_wet_surface', 'is_icy_surface', 'is_curve'
            ]
            
            # Ensure features exist
            available_features = [f for f in features if f in df.columns]
            target = 'severity'
            
            ml_df = df[available_features + [target]].dropna()
            
            logging.info(f"ML Dataset built. Shape: {ml_df.shape}")
            return ml_df
            
        except Exception as e:
            logging.error(f"Error building dataset: {e}")
            raise
        finally:
            conn.close()
