import folium
import json

def get_color(score):
    if score <= 20: return '#28a745'  # Green
    if score <= 40: return '#ffc107'  # Yellow
    if score <= 60: return '#fd7e14'  # Orange
    if score <= 80: return '#dc3545'  # Red
    return '#000000'                  # Black

def style_function(feature):
    score = feature['properties'].get('risk_score', 0)
    return {
        'fillColor': get_color(score),
        'color': '#ffffff',  # White border
        'weight': 1,
        'fillOpacity': 0.6
    }

def critical_style_function(feature):
    return {
        'fillColor': '#000000',
        'color': '#ff0000',  # Red glowing border
        'weight': 3,
        'fillOpacity': 0.8
    }

def top_zone_style_function(feature):
    return {
        'fillColor': 'transparent',
        'color': '#ffd700',  # Gold border
        'weight': 4,
        'fillOpacity': 0.0
    }

def create_risk_zone_layer(geojson_data, popup_builder):
    fg = folium.FeatureGroup(name="Risk Zones", show=True)
    folium.GeoJson(
        geojson_data,
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['h3_index', 'risk_score', 'risk_level'],
            aliases=['Zone:', 'Risk:', 'Level:'],
            localize=True,
            sticky=False,
            labels=True,
            style="""
                background-color: #F0EFEF;
                border: 2px solid black;
                border-radius: 3px;
                box-shadow: 3px;
            """,
            max_width=800,
        ),
        popup=folium.GeoJsonPopup(
            fields=['h3_index', 'risk_score', 'risk_level', 'risk_color', 'accident_count', 'fatal_count', 'peak_hour', 'explanation'],
            aliases=['Zone', 'Risk Score', 'Risk Level', 'Color', 'Accidents', 'Fatalities', 'Peak Hour', 'Why?'],
            labels=False # We will use custom HTML via iterating if needed, or stick to this built-in popup for simplicity
        )
    ).add_to(fg)
    return fg

def create_critical_zone_layer(geojson_data):
    # Filter only critical zones
    critical_features = [f for f in geojson_data['features'] if f['properties']['risk_score'] > 80]
    filtered_geojson = {"type": "FeatureCollection", "features": critical_features}
    
    fg = folium.FeatureGroup(name="Critical Zones (⚫)", show=False)
    folium.GeoJson(
        filtered_geojson,
        style_function=critical_style_function
    ).add_to(fg)
    return fg

def create_top_zones_layer(geojson_data, top_zones_list):
    # Filter top zones
    top_features = [f for f in geojson_data['features'] if f['properties']['h3_index'] in top_zones_list]
    filtered_geojson = {"type": "FeatureCollection", "features": top_features}
    
    fg = folium.FeatureGroup(name="Top 10 Dangerous Zones", show=False)
    folium.GeoJson(
        filtered_geojson,
        style_function=top_zone_style_function
    ).add_to(fg)
    return fg

def create_anomaly_layer(geojson_data, anomaly_list):
    # Filter anomaly zones
    anomaly_features = [f for f in geojson_data['features'] if f['properties']['h3_index'] in anomaly_list]
    filtered_geojson = {"type": "FeatureCollection", "features": anomaly_features}
    
    fg = folium.FeatureGroup(name="Anomaly Clusters (Isolation Forest)", show=False)
    # Give it a dashed blue border or something distinct
    folium.GeoJson(
        filtered_geojson,
        style_function=lambda x: {'fillColor': '#00ffff', 'color': '#00ffff', 'weight': 2, 'dashArray': '5, 5', 'fillOpacity': 0.5}
    ).add_to(fg)
    return fg

def create_vehicle_placeholder_layer():
    fg = folium.FeatureGroup(name="Real-Time Vehicles 🚗", show=False)
    # Placeholder: We will add dynamic markers here in Phase 6/7
    return fg
