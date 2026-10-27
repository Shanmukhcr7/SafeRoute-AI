import streamlit as st
import streamlit.components.v1 as components
import sqlite3
import pandas as pd
import json
import time
import math
import folium
from pathlib import Path
import sys

import sys
import h3

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from adas.route_analyzer import RouteAnalyzer
from context.context_engine import ContextEngine

st.set_page_config(page_title="AI Live Navigation", page_icon="🗺", layout="wide")

# --- INITIALIZATION ---
if 'simulation_state' not in st.session_state:
    st.session_state.simulation_state = "SETUP" # SETUP, RUNNING, FINISHED, REPLAY
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'selected_route_data' not in st.session_state:
    st.session_state.selected_route_data = None
if 'telemetry_log' not in st.session_state:
    st.session_state.telemetry_log = []
if 'speed_kmh' not in st.session_state:
    st.session_state.speed_kmh = 90
    
analyzer = RouteAnalyzer()
context_engine = ContextEngine()

def load_local_routes():
    routes = []
    candidates = [
        Path(__file__).resolve().parent.parent.parent / "routes",
        Path("routes"),
        Path("road-risk-ai/routes")
    ]
    routes_dir = next((c for c in candidates if c.exists()), Path("routes"))
    if routes_dir.exists():
        for f in routes_dir.glob("*.json"):
            with open(f, 'r', encoding="utf-8") as file:
                routes.append(json.load(file))
    return routes

# --- UI: SETUP PHASE ---
if st.session_state.simulation_state == "SETUP":
    st.title("🗺 AI Navigation Assistant")
    st.markdown("Select your destination. The AI will analyze historical road risk and recommend the safest route.")
    
    col1, col2 = st.columns(2)
    with col1:
        source = st.selectbox("Source", ["Paris"])
    with col2:
        dest = st.selectbox("Destination", ["Lyon", "Versailles", "Marseille"])
        
    routes = load_local_routes()
    if not routes:
        st.warning("No offline routes found in `routes/`. Please run the route fetcher script.")
        st.stop()
        
    st.subheader("🛣 Route Risk Analysis")
    
    st.markdown("### ☁ Environment Simulator (ML Engine)")
    col_w, col_t = st.columns(2)
    with col_w:
        weather = st.selectbox("Current Weather", ["Clear", "Rain", "Snow", "Fog"])
    with col_t:
        time_of_day = st.selectbox("Time of Day", ["Day", "Night"])
        
    st.session_state.weather = weather
    st.session_state.time_of_day = time_of_day
    
    # Compare Routes
    comparison_data = []
    best_route = None
    highest_safety = -1
    
    for r in routes:
        analysis = analyzer.analyze_route(r["geometry"], weather, time_of_day)
        r["analysis"] = analysis
        is_recommended = False
        
        if analysis["safety_score"] > highest_safety:
            highest_safety = analysis["safety_score"]
            best_route = r
            
        comparison_data.append({
            "Route": r["via"],
            "Distance": f"{r['distance_km']:.0f} km",
            "Time": f"{r['duration_minutes']/60:.1f} hrs",
            "Avg Risk": analysis["avg_risk"],
            "Critical Zones": analysis["critical_zones"],
            "Safety Score": analysis["safety_score"],
            "_raw": r
        })
        
    for cd in comparison_data:
        cd["Recommendation"] = "✅ Recommended" if cd["_raw"] == best_route else "❌ High Risk"
        
    df_compare = pd.DataFrame(comparison_data).drop(columns=["_raw"])
    st.dataframe(df_compare, use_container_width=True)
    
    # Risk Preview Timeline for the best route
    st.subheader(f"⭐ Risk Preview: {best_route['via']}")
    
    # Calculate hotspot counts for summary
    dz_summary = best_route["analysis"].get("dynamic_zones", {})
    count_fatal = len([z for z, d in dz_summary.items() if d["level"] == "FATAL"])
    count_critical = len([z for z, d in dz_summary.items() if d["level"] == "CRITICAL"])
    count_high = len([z for z, d in dz_summary.items() if d["level"] == "HIGH"])
    count_mod = len([z for z, d in dz_summary.items() if d["level"] == "MODERATE"])
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("🔴 Fatal Hotspots", count_fatal)
    col_m2.metric("🟥 Critical Hotspots", count_critical)
    col_m3.metric("🟧 High Hotspots", count_high)
    col_m4.metric("🟨 Moderate Hotspots", count_mod)

    # Route Hotspot Corridor Preview Map
    start_pt = best_route["geometry"][0]
    preview_map = folium.Map(location=[start_pt[1], start_pt[0]], zoom_start=8, tiles="OpenStreetMap")
    route_latlngs = [[p[1], p[0]] for p in best_route["geometry"]]
    folium.PolyLine(route_latlngs, color="#00aaff", weight=4, opacity=0.85, tooltip=f"Route: {best_route['via']}").add_to(preview_map)
    
    for z in best_route["analysis"]["passed_zones"]:
        if z in dz_summary and dz_summary[z]["level"] in ["FATAL", "CRITICAL", "HIGH", "MODERATE"]:
            poly = h3.cell_to_boundary(z)
            data = dz_summary[z]
            folium.Polygon(
                locations=poly,
                color=data["color"],
                fill=True,
                fill_color=data["color"],
                fill_opacity=0.6,
                weight=2,
                tooltip=f"{data['level']} Hotspot | AI Risk: {data['score']:.1f}/100"
            ).add_to(preview_map)
            
    components.html(preview_map._repr_html_(), height=400)
    
    st.markdown("---")
    col_start, col_speed = st.columns([1, 2])
    with col_speed:
        st.session_state.speed_kmh = st.slider("Simulated Speed (km/h)", 30, 150, 90)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Start Navigation", type="primary", use_container_width=True):
        st.session_state.current_route = best_route
        st.session_state.simulation_state = "RUNNING"
        st.session_state.current_step = 0
        st.rerun()

# --- UI: RUNNING SIMULATION ---
elif st.session_state.simulation_state == "RUNNING":
    route = st.session_state.current_route
    geom = route["geometry"]
    
    # Header
    st.markdown(f"## 🛰 Live Navigation: {route['via']}")
    
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.markdown("<p style='color:#00ff00; font-size:1.2rem;'>● LIVE</p>", unsafe_allow_html=True)
    with col_stat2:
        st.markdown(f"<p><strong>Environment:</strong> {st.session_state.weather} / {st.session_state.time_of_day} (ML Dynamic Risk Active)</p>", unsafe_allow_html=True)
        
    # The actual animation and telemetry is handled entirely by the JS component.
    # We just inject the HTML and wait for the user to click Finish.
    # Full width map without ADAS panel
    if st.session_state.simulation_state == "RUNNING":
        # Native JS Simulation Injection
        candidates = [
            Path(__file__).resolve().parent.parent / "components" / "smooth_simulator.html",
            Path("dashboard/components/smooth_simulator.html"),
            Path("road-risk-ai/dashboard/components/smooth_simulator.html"),
        ]
        html_path = next((c for c in candidates if c.exists()), Path("dashboard/components/smooth_simulator.html"))
        with open(html_path, "r", encoding="utf-8") as f:
            html_template = f.read()
            
        # Prepare data
        geom_json = json.dumps(geom)
        
        zones_data = []
        dynamic_zones = route["analysis"].get("dynamic_zones", {})
        
        for z in route["analysis"]["passed_zones"]:
            if z in dynamic_zones and dynamic_zones[z]["level"] in ["FATAL", "CRITICAL", "HIGH", "MODERATE"]:
                poly = h3.cell_to_boundary(z)
                poly_lonlat = [[p[1], p[0]] for p in poly] # JS turf needs lon,lat
                z_info = dynamic_zones[z]
                
                color = z_info.get("color")
                if not color:
                    color = "#EF4444" if z_info["level"] in ["FATAL", "CRITICAL"] else ("#F97316" if z_info["level"] == "HIGH" else "#FBBF24")
                
                zones_data.append({
                    "polygon": poly_lonlat, 
                    "color": color,
                    "level": z_info["level"],
                    "score": z_info["score"],
                    "base_score": z_info.get("base_score", z_info["score"]),
                    "multiplier": z_info.get("multiplier", 1.0)
                })
        
        zones_json = json.dumps(zones_data)
        
        # Inject
        final_html = html_template.replace("__ROUTE_GEOMETRY__", geom_json).replace("__RISK_ZONES__", zones_json)
        
        components.html(final_html, height=750)
        
        st.markdown("---")
        col_abort, col_finish = st.columns(2)
        with col_abort:
            if st.button("🛑 Abort Mission", use_container_width=True):
                st.session_state.simulation_state = "SETUP"
                st.rerun()
        with col_finish:
            if st.button("🏁 Finish Journey / View Report", use_container_width=True, type="primary"):
                st.session_state.simulation_state = "FINISHED"
                st.rerun()

# --- UI: FINISHED / TRIP REPORT ---
elif st.session_state.simulation_state == "FINISHED":
    st.title("🏁 Destination Reached")
    
    route = st.session_state.selected_route_data
    telemetry = st.session_state.telemetry_log
    
    avg_risk = sum([t["risk"] for t in telemetry]) / len(telemetry) if telemetry else 0
    max_risk = max([t["risk"] for t in telemetry]) if telemetry else 0
    critical_alerts = len([t for t in telemetry if t["level"] == "CRITICAL"])
    
    st.markdown("### 📊 Journey Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Distance", f"{route['distance_km']:.0f} km")
    col2.metric("Avg Risk", f"{avg_risk:.1f}")
    col3.metric("Max Risk", f"{max_risk:.0f}")
    col4.metric("Critical Alerts", critical_alerts)
    
    st.markdown("---")
    col_rep, col_home = st.columns(2)
    with col_rep:
        if st.button("▶ Replay Journey", type="primary", use_container_width=True):
            st.session_state.simulation_state = "REPLAY"
            st.session_state.current_step = 0
            st.rerun()
    with col_home:
        if st.button("🏠 New Journey", use_container_width=True):
            st.session_state.simulation_state = "SETUP"
            st.rerun()
