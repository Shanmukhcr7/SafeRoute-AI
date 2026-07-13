import pandas as pd
import numpy as np

def build_zone_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates individual accident features into H3 zone-level statistics."""
    
    # We want to group by h3_index and compute:
    # - accident_count: count of rows
    # - fatal_count: sum of fatalities
    # - rain_percentage: mean of is_rain * 100
    # - night_percentage: mean of is_night * 100
    # - severity_mean: mean of fatalities (or other severity metric)
    # - peak_hour: mode of hour
    # - road_surface_score: mean of is_wet_surface + is_icy_surface
    
    zone_stats = df.groupby('h3_index').agg(
        accident_count=('Num_Acc', 'count'),
        fatal_count=('fatalities', 'sum'),
        rain_percentage=('is_rain', lambda x: x.mean() * 100),
        night_percentage=('is_night', lambda x: x.mean() * 100),
        severity_mean=('fatalities', 'mean'),
        road_surface_score=('is_wet_surface', lambda x: x.mean() * 100),
        curve_percentage=('is_curve', lambda x: x.mean() * 100)
    ).reset_index()
    
    # Calculate peak hour
    # Mode can be slow, so we can calculate it separately and map it
    mode_hour = df.groupby('h3_index')['hour'].apply(lambda x: x.mode()[0] if not x.mode().empty else np.nan).reset_index()
    zone_stats = pd.merge(zone_stats, mode_hour, on='h3_index', how='left').rename(columns={'hour': 'peak_hour'})
    
    return zone_stats
