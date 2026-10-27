import joblib
import pandas as pd
import numpy as np
from pathlib import Path

class DynamicRiskPredictor:
    def __init__(self, model_path=None):
        if model_path is None:
            candidates = [
                Path(__file__).resolve().parent.parent / "models" / "dynamic_risk_model.pkl",
                Path("models/dynamic_risk_model.pkl"),
                Path("road-risk-ai/models/dynamic_risk_model.pkl"),
            ]
            self.model_path = next((c for c in candidates if c.exists()), Path("models/dynamic_risk_model.pkl"))
        else:
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
            'lat_rounded': round(lat, 1),
            'long_rounded': round(lon, 1),
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

    def get_risk_multipliers(self, coords_list, weather="Clear", time_of_day="Day"):
        """
        Vectorized batch calculation of risk multipliers for a list of (lat, lon) coordinates.
        Massively faster than calling get_risk_multiplier individually in loops.
        """
        if not self.model or not coords_list:
            return [1.0] * len(coords_list)

        is_raining = 1 if weather == "Rain" else 0
        is_snowing = 1 if weather == "Snow" else 0
        is_fog = 1 if weather == "Fog" else 0
        is_night = 1 if time_of_day == "Night" else 0
        hour = 2 if time_of_day == "Night" else 14

        n = len(coords_list)
        X_input = pd.DataFrame({
            'lat_rounded': [round(c[0], 1) for c in coords_list],
            'long_rounded': [round(c[1], 1) for c in coords_list],
            'is_raining': np.full(n, is_raining, dtype=np.int32),
            'is_snowing': np.full(n, is_snowing, dtype=np.int32),
            'is_fog': np.full(n, is_fog, dtype=np.int32),
            'is_night': np.full(n, is_night, dtype=np.int32),
            'hour': np.full(n, hour, dtype=np.int32)
        })

        probs = self.model.predict_proba(X_input)[:, 1]
        baseline_prob = 0.55
        multipliers = probs / baseline_prob
        return np.clip(multipliers, 0.5, 2.0).tolist()
