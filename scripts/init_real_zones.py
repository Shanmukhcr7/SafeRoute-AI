import pandas as pd
import h3
import sqlite3
from pathlib import Path
import json

def clean_coordinate(val):
    if pd.isna(val) or val == 0 or val == "0":
        return None
    try:
        val = str(val).replace(',', '.')
        num = float(val)
        # French dataset coordinates are sometimes divided by 100000
        if num > 1000 or num < -1000:
            num = num / 100000.0
        return num
    except:
        return None

def main():
    print("Loading French dataset...")
    df = pd.read_csv('data/raw/caracteristics.csv', encoding='latin1', low_memory=False)
    
    # Process coordinates
    df['lat'] = df['lat'].apply(clean_coordinate)
    df['long'] = df['long'].apply(clean_coordinate)
    
    # Filter bounds to roughly France
    df = df.dropna(subset=['lat', 'long'])
    df = df[(df['lat'] > 41) & (df['lat'] < 52) & (df['long'] > -6) & (df['long'] < 10)]
    
    print(f"Found {len(df)} valid GPS accidents in France.")
    
    if len(df) == 0:
        print("No valid coordinates found!")
        return
        
    print("Generating H3 Index...")
    df['h3_index'] = df.apply(lambda row: h3.latlng_to_cell(row['lat'], row['long'], 8), axis=1)
    
    print("Aggregating historical risk...")
    zone_stats = df.groupby('h3_index').size().reset_index(name='accident_count')
    
    # Normalize risk score 0-100 logically
    zone_stats['risk_score'] = zone_stats['accident_count'].apply(lambda x: min(x / 50.0 * 100, 100.0))
    
    # Determine risk level based on absolute severity for sparse ADAS mapping
    def get_level(count):
        if count > 40: return "FATAL"
        elif count > 20: return "CRITICAL"
        elif count > 10: return "HIGH"
        elif count > 5: return "MODERATE"
        else: return "SAFE"
        
    zone_stats['risk_level'] = zone_stats['accident_count'].apply(get_level)
    
    def get_color(level):
        if level == "FATAL": return "#000000" # Black
        elif level == "CRITICAL": return "#FF0000" # Red
        elif level == "HIGH": return "#FFA500" # Orange
        else: return "#FFFF00" # Yellow
        
    zone_stats['risk_color'] = zone_stats['risk_level'].apply(get_color)
    zone_stats['risk_color'] = zone_stats['risk_level'].apply(get_color)
    zone_stats['explanation'] = zone_stats['accident_count'].apply(lambda x: f"{x} historical accidents.")
    zone_stats['ai_prediction'] = zone_stats['risk_score'] # Mock AI for now
    
    print(f"Connecting to database to store {len(zone_stats)} zones...")
    conn = sqlite3.connect('database/road_risk.db')
    zone_stats.to_sql('risk_scores', conn, if_exists='replace', index=False)
    
    # Also create the risk_zones table (geometry cache if needed, but we can compute live)
    conn.close()
    print("Done! Database populated with authentic French H3 zones.")

if __name__ == "__main__":
    main()
