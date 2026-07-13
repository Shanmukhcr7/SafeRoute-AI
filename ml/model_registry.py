import joblib
import json
import logging
from pathlib import Path
import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ModelRegistry:
    """Handles saving and loading models and metadata."""
    
    def __init__(self, registry_dir: str = "models"):
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        
    def save_model(self, model, model_name: str, features: list, metrics_df, version: str = "1.0"):
        logging.info(f"Saving {model_name} to registry...")
        
        # Save Pickle
        model_path = self.registry_dir / f"{model_name.lower().replace(' ', '_')}.pkl"
        joblib.dump(model, model_path)
        
        # Save Metadata
        best_metrics = metrics_df[metrics_df['Model'] == model_name].iloc[0]
        metadata = {
            "model_name": model_name,
            "version": version,
            "training_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "features": features,
            "accuracy": float(best_metrics['Accuracy']),
            "f1_score": float(best_metrics['F1 Score'])
        }
        
        meta_path = self.registry_dir / "metadata.json"
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=4)
            
        # Save comparison table
        metrics_df.to_csv(self.registry_dir / "model_comparison.csv", index=False)
        
        logging.info(f"Model and Metadata saved successfully in {self.registry_dir}")

    def load_best_model(self):
        try:
            meta_path = self.registry_dir / "metadata.json"
            with open(meta_path, 'r') as f:
                metadata = json.load(f)
            
            model_name = metadata['model_name'].lower().replace(' ', '_')
            model_path = self.registry_dir / f"{model_name}.pkl"
            
            model = joblib.load(model_path)
            return model, metadata['features']
        except Exception as e:
            logging.error(f"Error loading model from registry: {e}")
            raise
