import requests
import json
import os

def fetch_osrm_route(name, coordinates, via="Direct"):
    print(f"Fetching {name} (via {via})...")
    
    # Format coordinates string
    coords_str = ";".join([f"{lon},{lat}" for lon, lat in coordinates])
    
    # OSRM public API (driving) with geometries=geojson
    url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["code"] == "Ok":
            route = data["routes"][0]
            
            # Reformat into a clean structure for our UI
            clean_data = {
                "route_name": name,
                "via": via,
                "distance_km": route["distance"] / 1000.0,
                "duration_minutes": route["duration"] / 60.0,
                "geometry": route["geometry"]["coordinates"] # list of [lon, lat]
            }
            
            filepath = f"routes/{name}.json"
            with open(filepath, 'w') as f:
                json.dump(clean_data, f)
            print(f"Saved {filepath}")
        else:
            print(f"OSRM Error: {data['code']}")
    else:
        print(f"HTTP Error: {response.status_code}")

def main():
    os.makedirs("routes", exist_ok=True)
    
    paris = (2.3522, 48.8566)
    lyon = (4.8357, 45.7640)
    dijon = (5.0415, 47.3220)
    clermont = (3.0870, 45.7772)
    
    # Route A: Direct (A6 highway)
    fetch_osrm_route("paris_lyon_A", [paris, lyon], "A6 Highway (Direct)")
    
    # Route B: Via Dijon
    fetch_osrm_route("paris_lyon_B", [paris, dijon, lyon], "Dijon (Scenic)")
    
    # Route C: Via Clermont-Ferrand
    fetch_osrm_route("paris_lyon_C", [paris, clermont, lyon], "Clermont-Ferrand (Western)")

if __name__ == "__main__":
    main()
