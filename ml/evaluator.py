import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ModelEvaluator:
    """Evaluates the model and generates dashboard-ready metrics."""
    
    def __init__(self, model, X_test, y_test, feature_names):
        self.model = model
        self.X_test = X_test
        self.y_test = y_test
        self.feature_names = feature_names
        
    def generate_evaluation_report(self, output_dir: str = "models/evaluation"):
        logging.info("Generating Model Evaluation Dashboard Data...")
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        preds = self.model.predict(self.X_test)
        probas = self.model.predict_proba(self.X_test)
        
        # 1. Confusion Matrix
        cm = confusion_matrix(self.y_test, preds).tolist()
        
        # 2. Classification Report (Precision, Recall, F1)
        cr = classification_report(self.y_test, preds, output_dict=True)
        
        # 3. Feature Importance
        importances = getattr(self.model, "feature_importances_", [])
        feat_imp = []
        if len(importances) > 0:
            for f, imp in zip(self.feature_names, importances):
                feat_imp.append({"feature": f, "importance": float(imp)})
            feat_imp = sorted(feat_imp, key=lambda x: x['importance'], reverse=True)
            
        # 4. ROC Curve Data (For class 3 / Fatal vs Rest as an example)
        # Binarize for Fatal
        y_test_bin = (self.y_test == 3).astype(int)
        if probas.shape[1] > 3:
            fpr, tpr, _ = roc_curve(y_test_bin, probas[:, 3])
            roc_auc = auc(fpr, tpr)
            roc_data = {"fpr": fpr.tolist(), "tpr": tpr.tolist(), "auc": roc_auc}
        else:
            roc_data = {}
            
        report = {
            "confusion_matrix": cm,
            "classification_report": cr,
            "feature_importance": feat_imp,
            "roc_fatal": roc_data
        }
        
        with open(out_path / "evaluation_report.json", 'w') as f:
            json.dump(report, f, indent=4)
            
        logging.info("Evaluation report saved successfully.")
        return report
