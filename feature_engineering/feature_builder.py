import sys
import h3
import json
from pathlib import Path
import logging

sys.path.append(str(Path(__file__).resolve().parent.parent))
from database.sqlite import DatabaseManager
from feature_engineering.temporal_features import extract_temporal_features
from feature_engineering.weather_features import extract_weather_features
from feature_engineering.zone_statistics import build_zone_statistics
from feature_engineering.normalization import normalize_features
from feature_engineering.risk_engine import RiskEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class FeatureBuilder:
    def __init__(self, db_path: str = "database/road_risk.db"):
        self.db_manager = DatabaseManager(db_path)
        
    def load_base_data(self):
        logging.info("Loading processed accidents from SQLite...")
        query = "SELECT * FROM processed_accidents"
        return self.db_manager.load_dataframe(query)
        
    def build_features(self):
        df = self.load_base_data()
        
        logging.info("Extracting temporal features...")
        df = extract_temporal_features(df)
        
        logging.info("Extracting weather features...")
        df = extract_weather_features(df)
        
        logging.info("Building zone-level statistics...")
        zone_stats = build_zone_statistics(df)
        
        logging.info("Normalizing features...")
        zone_stats = normalize_features(zone_stats, ['accident_count', 'fatal_count'])
        # Rename to match RiskEngine expectations
        zone_stats.rename(columns={'accident_count': 'norm_accident_count', 'fatal_count': 'norm_fatal_count'}, inplace=True)
        
        logging.info("Running Risk Intelligence Engine...")
        engine = RiskEngine(zone_stats)
        scored_zones = engine.calculate_hybrid_score()
        scored_zones = engine.generate_explanations(scored_zones)
        
        # Save Outputs
        processed_dir = Path("data/processed")
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        logging.info("Saving zone statistics and risk scores to CSV...")
        scored_zones.to_csv(processed_dir / "zone_statistics.csv", index=False)
        scored_zones[['h3_index', 'risk_score', 'risk_level', 'risk_color', 'explanation']].to_csv(processed_dir / "risk_scores.csv", index=False)
        df.to_csv(processed_dir / "processed_features.csv", index=False)
        
        logging.info("Saving to SQLite Risk Tables...")
        self.db_manager.save_dataframe(scored_zones, "zone_statistics")
        self.db_manager.save_dataframe(scored_zones[['h3_index', 'risk_score', 'risk_level', 'risk_color', 'explanation']], "risk_scores")
        
        logging.info("Generating GeoJSON mapping for GIS...")
        self.generate_geojson(scored_zones, processed_dir / "risk_zone.geojson")
        
        logging.info("Phase 2 Complete! Risk Intelligence Engine successfully generated.")
        
    def generate_geojson(self, df, output_path):
        features = []
        for _, row in df.iterrows():
            h3_idx = row['h3_index']
            # Get hexagon boundary coordinates (h3 returns lat, lon; GeoJSON wants lon, lat)
            boundary = h3.h3_to_geo_boundary(h3_idx, geo_json=True)
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [boundary]
                },
                "properties": {
                    "h3_index": h3_idx,
                    "risk_score": row['risk_score'],
                    "risk_level": row['risk_level'],
                    "risk_color": row['risk_color'],
                    "explanation": row['explanation']
                }
            }
            features.append(feature)
            
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        with open(output_path, 'w') as f:
            json.dump(geojson, f)
            
if __name__ == "__main__":
    builder = FeatureBuilder()
    builder.build_features()
