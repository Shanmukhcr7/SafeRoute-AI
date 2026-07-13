import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def normalize_features(df: pd.DataFrame, columns_to_normalize: list) -> pd.DataFrame:
    """
    Normalizes a list of features to the 0-100 scale using Min-Max scaling.
    This prepares the raw metrics for the final Risk Score Engine.
    """
    try:
        scaler = MinMaxScaler(feature_range=(0, 100))
        df[columns_to_normalize] = scaler.fit_transform(df[columns_to_normalize])
    except Exception as e:
        print(f"Error normalizing features: {e}")
        
    return df
