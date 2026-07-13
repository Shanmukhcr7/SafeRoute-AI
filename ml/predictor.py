import pandas as pd
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from ml.model_registry import ModelRegistry
from ml.shap_explainer import ShapExplainer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class RiskPredictorAPI:
    """API for the Streamlit Dashboard and Dynamic Map to get AI predictions."""
    
    def __init__(self):
        self.registry = ModelRegistry()
        try:
            self.model, self.features = self.registry.load_best_model()
            self.explainer = ShapExplainer(self.model, self.features)
            logging.info("Predictor API Initialized successfully.")
        except Exception as e:
            logging.warning("Model not found in registry. Please run Phase 5 training pipeline first.")
            self.model = None
            
    def predict(self, input_data: dict) -> dict:
        """
        Takes raw condition inputs, formats them for the model, and returns severity prediction.
        input_data = {'is_rain': 1, 'hour': 18, 'is_night': 1, 'is_curve': 1, ...}
        """
        if self.model is None:
            return {"error": "Model not trained yet."}
            
        # Create DataFrame ensuring all required features exist
        df_input = pd.DataFrame([input_data])
        
        # Fill missing features with 0 (safe default)
        for f in self.features:
            if f not in df_input.columns:
                df_input[f] = 0
                
        # Reorder to match training
        df_input = df_input[self.features]
        
        # Get explanation and prediction
        result = self.explainer.explain_prediction(df_input)
        
        return result
        
    def calculate_dynamic_risk(self, historical_risk: float, ai_severity_prediction: str) -> float:
        """
        Combines Historical Risk + AI Severity Prediction.
        """
        severity_multiplier = {
            "Safe": 1.0,
            "Low Risk": 1.1,
            "Moderate Risk": 1.25,
            "High Risk": 1.5
        }
        
        multiplier = severity_multiplier.get(ai_severity_prediction, 1.0)
        dynamic_risk = historical_risk * multiplier
        
        return min(dynamic_risk, 100.0)
