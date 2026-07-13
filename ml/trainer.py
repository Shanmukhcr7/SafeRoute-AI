import pandas as pd
import logging
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, f1_score
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ModelTrainer:
    """Trains and compares multiple machine learning models."""
    
    def __init__(self):
        self.models = {
            "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
            "XGBoost": XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, use_label_encoder=False, eval_metric='mlogloss')
        }
        # Try importing LightGBM, add if available
        try:
            import lightgbm as lgb
            self.models["LightGBM"] = lgb.LGBMClassifier(n_estimators=100, max_depth=6, random_state=42)
        except ImportError:
            logging.info("LightGBM not installed, skipping.")

    def train_and_compare(self, X: pd.DataFrame, y: pd.Series):
        logging.info("Splitting dataset into Train/Test (80/20)...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        results = []
        best_model = None
        best_f1 = 0
        best_name = ""
        
        for name, model in self.models.items():
            logging.info(f"Training {name}...")
            start_time = time.time()
            model.fit(X_train, y_train)
            train_time = time.time() - start_time
            
            preds = model.predict(X_test)
            acc = accuracy_score(y_test, preds)
            # Weighted F1 for multiclass
            f1 = f1_score(y_test, preds, average='weighted')
            
            results.append({
                "Model": name,
                "Accuracy": acc,
                "F1 Score": f1,
                "Training Time (s)": round(train_time, 2)
            })
            
            if f1 > best_f1:
                best_f1 = f1
                best_model = model
                best_name = name
                
        results_df = pd.DataFrame(results)
        logging.info(f"\nModel Comparison:\n{results_df.to_markdown(index=False)}")
        logging.info(f"Best Model: {best_name} (F1: {best_f1:.4f})")
        
        return best_model, best_name, X_train, X_test, y_train, y_test, results_df
