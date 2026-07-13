import pandas as pd

def extract_weather_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extracts weather specific binary features from the 'atm' column."""
    # atm: 1=Normal, 2=Light rain, 3=Heavy rain, 4=Snow, 5=Fog, 6=Wind, etc.
    try:
        df['is_rain'] = df['atm'].apply(lambda x: 1 if x in [2, 3] else 0)
        df['is_snow'] = df['atm'].apply(lambda x: 1 if x == 4 else 0)
        df['is_fog'] = df['atm'].apply(lambda x: 1 if x == 5 else 0)
        df['is_wind'] = df['atm'].apply(lambda x: 1 if x == 6 else 0)
        df['bad_weather'] = df['atm'].apply(lambda x: 1 if x > 1 else 0)
        
        # Road Surface (surf): 1=Normal, 2=Wet, 3=Puddles, 4=Flooded, 5=Snow/Ice
        df['is_wet_surface'] = df['surf'].apply(lambda x: 1 if x in [2, 3, 4] else 0)
        df['is_icy_surface'] = df['surf'].apply(lambda x: 1 if x == 5 else 0)
        
        # Road Geometry (prof): Curve, Straight, Slope
        # prof: 1=Flat, 2=Slope, 3=Hill, 4=Bottom
        # plan: 1=Straight, 2=Curve left, 3=Curve right, 4='S'
        df['is_curve'] = df['plan'].apply(lambda x: 1 if x in [2, 3, 4] else 0)
        
    except Exception as e:
        print(f"Error extracting weather features: {e}")
        
    return df
