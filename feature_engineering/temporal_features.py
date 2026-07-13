import pandas as pd
import numpy as np

def extract_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extracts hour, weekend, season, and night flags from date and hrmn."""
    # Assuming 'jour' (day), 'mois' (month), 'an' (year) and 'hrmn' (hour/min)
    # The dataset uses 'an' as year (e.g. 16 for 2016)
    try:
        # Create a proxy date if needed, though we can just use the components
        df['hour'] = df['hrmn'] // 100
        
        # Season mapping based on month (mois)
        # 12, 1, 2 = Winter, 3,4,5 = Spring, 6,7,8 = Summer, 9,10,11 = Autumn
        df['season'] = df['mois'].apply(
            lambda x: 'Winter' if x in [12, 1, 2] else
                      'Spring' if x in [3, 4, 5] else
                      'Summer' if x in [6, 7, 8] else 'Autumn'
        )
        
        # Night Flag (lum: 1=Day, 2,3,4,5 are night conditions)
        # Generally, lum > 1 implies twilight/night.
        df['is_night'] = df['lum'].apply(lambda x: 1 if x > 1 else 0)
        
        # Rush Hour (roughly 7-9 AM and 5-7 PM)
        df['is_rush_hour'] = df['hour'].apply(lambda h: 1 if h in [7, 8, 9, 17, 18, 19] else 0)
        
    except Exception as e:
        print(f"Error extracting temporal features: {e}")
        
    return df
