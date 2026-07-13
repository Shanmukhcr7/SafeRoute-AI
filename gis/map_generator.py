import folium
from folium.plugins import Search, Fullscreen
import json
import sqlite3
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))
from gis.layer_manager import (
    create_risk_zone_layer, 
    create_critical_zone_layer, 
    create_top_zones_layer, 
    create_anomaly_layer,
    create_vehicle_placeholder_layer
)
from gis.legend import build_analytics_panel
from gis.popup_builder import build_risk_popup

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class MapGenerator:
    def __init__(self, geojson_path: str = "data/processed/risk_zone.geojson", db_path: str = "database/road_risk.db"):
        self.geojson_path = Path(geojson_path)
        self.db_path = Path(db_path)
        
    def load_data(self):
        logging.info("Loading GeoJSON and SQLite data...")
        with open(self.geojson_path, 'r') as f:
            self.geojson_data = json.load(f)
            
        conn = sqlite3.connect(self.db_path)
        # We need accident_count, peak_hour, etc for the popup mapping if not perfectly inside GeoJSON
        # But we wrote them to GeoJSON in Phase 2? Wait, Phase 2 feature_builder wrote:
        # h3_index, risk_score, risk_level, risk_color, explanation
        # Let's enrich the geojson properties natively here with SQLite data to ensure full popup support
        
        cursor = conn.cursor()
        cursor.execute("SELECT h3_index, accident_count, fatal_count, peak_hour FROM zone_statistics")
        stats = {row[0]: {'accident_count': row[1], 'fatal_count': row[2], 'peak_hour': row[3]} for row in cursor.fetchall()}
        
        self.top_zones = [row[0] for row in cursor.execute("SELECT h3_index FROM top_dangerous_zones LIMIT 10").fetchall()]
        conn.close()
        
        # Load Anomalies JSON
        try:
            with open("data/processed/analytics/anomalies.json", 'r') as f:
                self.anomalies = [a['h3_index'] for a in json.load(f)]
        except:
            self.anomalies = []

        # Enrich geojson
        for feature in self.geojson_data['features']:
            h3_id = feature['properties']['h3_index']
            stat = stats.get(h3_id, {})
            feature['properties']['accident_count'] = stat.get('accident_count', 0)
            feature['properties']['fatal_count'] = stat.get('fatal_count', 0)
            feature['properties']['peak_hour'] = stat.get('peak_hour', 'N/A')
            
            # Create custom HTML popup string
            feature['properties']['custom_popup'] = build_risk_popup(feature['properties'])
            
    def generate_map(self, output_path: str = "interactive_risk_map.html"):
        logging.info("Initializing Map...")
        # Center map over France roughly
        m = folium.Map(location=[46.2276, 2.2137], zoom_start=6, tiles='CartoDB dark_matter')
        
        logging.info("Building Layers...")
        # We use a trick: Folium GeoJsonPopup cannot easily render raw HTML strings from a property perfectly without custom JS sometimes,
        # but passing it via iframe or just using the built in properties works. 
        # For simplicity and robustness, we use folium.GeoJson with a tooltip and native fields.
        
        risk_layer = create_risk_zone_layer(self.geojson_data, popup_builder=build_risk_popup)
        critical_layer = create_critical_zone_layer(self.geojson_data)
        top_layer = create_top_zones_layer(self.geojson_data, self.top_zones)
        anomaly_layer = create_anomaly_layer(self.geojson_data, self.anomalies)
        vehicle_layer = create_vehicle_placeholder_layer()
        
        risk_layer.add_to(m)
        critical_layer.add_to(m)
        top_layer.add_to(m)
        anomaly_layer.add_to(m)
        vehicle_layer.add_to(m)
        
        # Add Search Plugin (Searching by h3_index property)
        # Note: Search plugin requires the layer to be passed.
        # We use risk_layer (which is a FeatureGroup containing the GeoJson child)
        # We must extract the GeoJson child to pass to Search.
        geojson_child = None
        for key, val in risk_layer._children.items():
            if isinstance(val, folium.features.GeoJson):
                geojson_child = val
                break
                
        if geojson_child:
            Search(
                layer=geojson_child,
                geom_type='Polygon',
                placeholder='Search Zone ID...',
                collapsed=False,
                search_label='h3_index'
            ).add_to(m)
        
        # Add Analytics Panel & Legend
        critical_count = len([f for f in self.geojson_data['features'] if f['properties']['risk_score'] > 80])
        total_count = len(self.geojson_data['features'])
        avg_risk = sum([f['properties']['risk_score'] for f in self.geojson_data['features']]) / total_count if total_count > 0 else 0
        
        stats = {
            'total_zones': total_count,
            'critical_zones': critical_count,
            'avg_risk': avg_risk
        }
        
        panel = build_analytics_panel(stats)
        m.get_root().add_child(panel)
        
        # Fullscreen and LayerControl
        Fullscreen().add_to(m)
        folium.LayerControl(collapsed=False).add_to(m)
        
        logging.info(f"Saving interactive map to {output_path}...")
        m.save(output_path)
        logging.info("Map generated successfully!")

if __name__ == "__main__":
    generator = MapGenerator()
    generator.load_data()
    generator.generate_map()
