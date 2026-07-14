import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, roc_curve
from sklearn.inspection import permutation_importance
import json

def train_model():
    print("[1/5] Loading datasets for ML Training...")
    
    # 1. Load Characteristics (Environment & Location)
    df_carac = pd.read_csv('data/raw/caracteristics.csv', encoding='latin1', low_memory=False)
    
    # 2. Load Users (Accident Severity)
    df_users = pd.read_csv('data/raw/users.csv', encoding='latin1', low_memory=False)
    
    print("[2/5] Merging datasets...")
    # Group users by accident to find the maximum severity of the accident
    # grav: 1=Unharmed, 2=Killed, 3=Hospitalized, 4=Light injury
    # We map Killed (2) and Hospitalized (3) as Severe (1), else Non-Severe (0)
    df_users['is_severe'] = df_users['grav'].isin([2, 3]).astype(int)
    accident_severity = df_users.groupby('Num_Acc')['is_severe'].max().reset_index()
    
    # Merge with characteristics
    df = pd.merge(df_carac, accident_severity, on='Num_Acc', how='inner')
    
    print("[3/5] Engineering Features...")
    
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['long'] = pd.to_numeric(df['long'], errors='coerce')
    df = df[(df['lat'] != 0) & (df['long'] != 0)]
    df = df.dropna(subset=['lat', 'long'])
    
    # Fix the 100000 multiplier commonly found in French accident datasets
    df.loc[df['lat'] > 90, 'lat'] = df['lat'] / 100000
    df.loc[df['long'] > 180, 'long'] = df['long'] / 100000
    df.loc[df['long'] < -180, 'long'] = df['long'] / 100000
    
    # Ensure lat/lon are within France boundaries
    df = df[(df['lat'] > 41) & (df['lat'] < 52) & (df['long'] > -5) & (df['long'] < 10)]
    
    # Features
    # atm: 1=Normal, 2=Light rain, 3=Heavy rain, 4=Snow, 8=Fog
    df['is_raining'] = df['atm'].isin([2, 3]).astype(int)
    df['is_snowing'] = (df['atm'] == 4).astype(int)
    df['is_fog'] = (df['atm'] == 8).astype(int)
    
    # lum: 1=Daylight, 3=Night without lighting, 4=Night with lighting off, 5=Night with lighting on
    df['is_night'] = df['lum'].isin([3, 4, 5]).astype(int)
    
    # Extract Hour
    def extract_hour(val):
        try:
            val_str = str(val)
            if ':' in val_str:
                return int(val_str.split(':')[0])
            else:
                return int(val_str[:-2]) if len(val_str) >= 3 else int(val_str)
        except:
            return 12 # fallback to noon
            
    df['hour'] = df['hrmn'].apply(extract_hour)
    
    features = ['is_raining', 'is_snowing', 'is_fog', 'is_night', 'hour']
    X = df[features]
    y = df['is_severe']
    
    print(f"[4/5] Training on {len(X)} accident records...")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Use HistGradientBoostingClassifier because it is insanely fast and handles NaN values perfectly
    clf = HistGradientBoostingClassifier(max_iter=100, learning_rate=0.1, random_state=42)
    
    print("[5/5] Training HistGradientBoostingClassifier...")
    clf.fit(X_train, y_train)
    
    print("Evaluating Model...")
    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]
    
    print("\nClassification Report:")
    report = classification_report(y_test, y_pred, output_dict=True)
    print(classification_report(y_test, y_pred))
    auc = roc_auc_score(y_test, y_prob)
    print(f"ROC-AUC Score: {auc:.4f}")
    
    print("Calculating Feature Importance...")
    perm_importance = permutation_importance(clf, X_test, y_test, n_repeats=5, random_state=42)
    feat_imp = [{"feature": f, "importance": float(i)} for f, i in zip(features, perm_importance.importances_mean)]
    
    cm = confusion_matrix(y_test, y_pred)
    
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    
    # Save the model
    os.makedirs('models/evaluation', exist_ok=True)
    joblib.dump(clf, 'models/dynamic_risk_model.pkl')
    print("Model successfully saved to models/dynamic_risk_model.pkl")
    
    eval_data = {
        "classification_report": report,
        "roc_fatal": {"auc": auc, "fpr": fpr.tolist()[::10], "tpr": tpr.tolist()[::10]},
        "confusion_matrix": cm.tolist(),
        "feature_importance": sorted(feat_imp, key=lambda x: x["importance"], reverse=True)
    }
    
    with open('models/evaluation/evaluation_report.json', 'w') as f:
        json.dump(eval_data, f)
        
    meta_data = {
        "model_type": "HistGradientBoostingClassifier",
        "dataset_size": len(X),
        "target": "Severe Accident Probability",
        "features": features,
        "accuracy": report['accuracy']
    }
    
    with open('models/metadata.json', 'w') as f:
        json.dump(meta_data, f)
        
    print("Graphs and Analytics saved to JSON for the Dashboard!")

if __name__ == "__main__":
    train_model()
