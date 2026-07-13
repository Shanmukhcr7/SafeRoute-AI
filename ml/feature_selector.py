import pandas as pd
from sklearn.feature_selection import VarianceThreshold, RFE
from sklearn.ensemble import RandomForestClassifier
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class FeatureSelector:
    """Performs Feature Selection using Variance, Correlation, and RFE."""
    
    def __init__(self, n_features_to_select: int = 10):
        self.n_features = n_features_to_select
        
    def select_features(self, X: pd.DataFrame, y: pd.Series) -> list:
        logging.info("Starting Feature Selection process...")
        
        # 1. Variance Threshold (Remove constant features)
        logging.info("Applying Variance Threshold...")
        var_selector = VarianceThreshold(threshold=0.01)
        var_selector.fit(X)
        X_var = X.loc[:, var_selector.get_support()]
        logging.info(f"Features remaining after Variance Threshold: {X_var.shape[1]}")
        
        # 2. Correlation Filter (Remove highly correlated features to prevent multicollinearity)
        logging.info("Applying Correlation Filter...")
        corr_matrix = X_var.corr().abs()
        upper = corr_matrix.where(pd.np.triu(pd.np.ones(corr_matrix.shape), k=1).astype(bool))
        to_drop = [column for column in upper.columns if any(upper[column] > 0.85)]
        X_corr = X_var.drop(columns=to_drop)
        logging.info(f"Features remaining after Correlation Filter: {X_corr.shape[1]}")
        
        # 3. Recursive Feature Elimination (RFE)
        logging.info("Applying Recursive Feature Elimination (RFE) with Random Forest...")
        estimator = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
        rfe = RFE(estimator, n_features_to_select=min(self.n_features, X_corr.shape[1]), step=1)
        rfe.fit(X_corr, y)
        
        selected_features = X_corr.columns[rfe.support_].tolist()
        logging.info(f"Final Selected Features: {selected_features}")
        
        return selected_features
