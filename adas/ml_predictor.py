import joblib
import pandas as pd
import numpy as np
from pathlib import Path

class DynamicRiskPredictor:
    def __init__(self, model_path="models/dynamic_risk_model.pkl"):
        self.model_path = Path(model_path)
        self.model = None
        if self.model_path.exists():
            self.model = joblib.load(self.model_path)
            
    def get_risk_multiplier(self, lat, lon, weather="Clear", time_of_day="Day"):
        """
        Returns a risk multiplier based on ML prediction.
        E.g. 1.0 means average risk. 1.5 means 50% higher risk of a severe accident.
        """
        if not self.model:
            return 1.0 # fallback if model not loaded
            
        # Feature Mapping
        is_raining = 1 if weather == "Rain" else 0
        is_snowing = 1 if weather == "Snow" else 0
        is_fog = 1 if weather == "Fog" else 0
        is_night = 1 if time_of_day == "Night" else 0
        hour = 2 if time_of_day == "Night" else 14 # Approx hour
        
        # Create input dataframe matching training features
        X_input = pd.DataFrame([{
            'is_raining': is_raining,
            'is_snowing': is_snowing,
            'is_fog': is_fog,
            'is_night': is_night,
            'hour': hour
        }])
        
        # Predict probability of severe accident (Class 1)
        prob_severe = self.model.predict_proba(X_input)[0][1]
        
        # Baseline severity probability across France is approx 55% in this dataset
        baseline_prob = 0.55
        
        # Multiplier based on relative risk vs baseline
        multiplier = prob_severe / baseline_prob
        
        # Cap multiplier between 0.5 (very safe) and 2.0 (extremely dangerous)
        return max(0.5, min(multiplier, 2.0))
