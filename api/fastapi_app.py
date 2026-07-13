from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import json
import requests
import h3
import sqlite3
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from adas.route_analyzer import RouteAnalyzer

app = FastAPI(
    title="Road Risk AI API",
    description="Backend for the React Dashboard",
    version="1.0.0"
)

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Analyzer
try:
    analyzer = RouteAnalyzer()
    print("✅ Route Analyzer initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Route Analyzer: {e}")
    analyzer = None

class RouteRequest(BaseModel):
    origin_lat: float
    origin_lon: float
    dest_lat: float
    dest_lon: float
    weather: str = "Clear"
    time_of_day: str = "Day"

@app.post("/api/analyze-route")
def analyze_route(req: RouteRequest):
    if not analyzer:
        raise HTTPException(status_code=500, detail="Analyzer not initialized")
        
    # 1. Fetch OSRM Route
    url = f"http://router.project-osrm.org/route/v1/driving/{req.origin_lon},{req.origin_lat};{req.dest_lon},{req.dest_lat}?geometries=geojson&overview=full"
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch route from OSRM")
        
    data = response.json()
    if data["code"] != "Ok":
        raise HTTPException(status_code=400, detail="No route found")
        
    route = data["routes"][0]
    geometry = route["geometry"]["coordinates"] # List of [lon, lat]
    distance_km = route["distance"] / 1000.0
    
    # 2. Analyze Route
    analysis = analyzer.analyze_route(geometry, req.weather, req.time_of_day)
    
    # Inject H3 polygons for React map to draw
    for zone_id, zdata in analysis["dynamic_zones"].items():
        if zdata["level"] in ["FATAL", "CRITICAL", "HIGH"]:
            poly = h3.cell_to_boundary(zone_id)
            zdata["polygon"] = poly # List of [lat, lon]
            
            # Fallback color formatting
            if zdata["level"] == "FATAL":
                zdata["color"] = "#FF0000" # Red
            elif zdata["level"] == "CRITICAL":
                zdata["color"] = "#000000" # Black
            elif zdata["level"] == "HIGH":
                zdata["color"] = "#FFFF00" # Yellow
                
    return {
        "distance_km": distance_km,
        "geometry": geometry,
        "analysis": analysis
    }

@app.get("/api/analytics")
def get_analytics():
    try:
        with open("models/evaluation/evaluation_report.json", 'r') as f:
            eval_data = json.load(f)
        with open("models/metadata.json", 'r') as f:
            meta_data = json.load(f)
        return {"eval_data": eval_data, "meta_data": meta_data}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Analytics data not found: {e}")

@app.get("/api/france-risk-map")
def get_france_risk_map():
    db_path = Path("database/road_risk.db")
    if not db_path.exists():
        raise HTTPException(status_code=500, detail="Database not found")
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Fetch Top 1000 most dangerous spots
    cursor.execute("SELECT h3_index, risk_score, risk_level, risk_color FROM risk_scores ORDER BY risk_score DESC LIMIT 1000")
    rows = cursor.fetchall()
    conn.close()
    
    zones = []
    for r in rows:
        zone_id = r[0]
        level = r[2]
        color = r[3]
        poly = h3.cell_to_boundary(zone_id)
        
        # Color corrections for modern dark map
        if level == "FATAL":
            color = "#FF0000" # Red
        elif level == "CRITICAL":
            color = "#000000" # Black
        elif level == "HIGH":
            color = "#FFFF00" # Yellow
            
        # Flip coordinates from (lat, lon) to [lat, lon] for Leaflet
        zones.append({
            "zone_id": zone_id,
            "score": r[1],
            "level": level,
            "color": color,
            "polygon": poly
        })
    return {"zones": zones}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
