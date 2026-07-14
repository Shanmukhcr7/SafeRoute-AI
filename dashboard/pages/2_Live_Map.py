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
    routes_dir = Path("routes")
    if routes_dir.exists():
        for f in routes_dir.glob("*.json"):
            with open(f, 'r') as file:
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
    
    # Simple mock timeline for demo
    timeline_html = f"""
    <div style="width:100%; background:#333; height:20px; border-radius:10px; display:flex; overflow:hidden;">
        <div style="width:30%; background:#28a745; height:100%;" title="Safe"></div>
        <div style="width:20%; background:#ffc107; height:100%;" title="Moderate Risk"></div>
        <div style="width:15%; background:#dc3545; height:100%;" title="Critical Zone"></div>
        <div style="width:35%; background:#28a745; height:100%;" title="Safe"></div>
    </div>
    <div style="display:flex; justify-content:space-between; color:#aaa; font-size:0.8rem; margin-top:5px;">
        <span>0 km</span>
        <span>{best_route['distance_km']:.0f} km</span>
    </div>
    """
    st.markdown(timeline_html, unsafe_allow_html=True)
    
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
        with open("dashboard/components/smooth_simulator.html", "r", encoding="utf-8") as f:
            html_template = f.read()
            
        # Prepare data
        geom_json = json.dumps(geom)
        
        zones_data = []
        dynamic_zones = route["analysis"].get("dynamic_zones", {})
        
        for z in route["analysis"]["passed_zones"]:
            if z in dynamic_zones and dynamic_zones[z]["level"] in ["FATAL", "CRITICAL", "HIGH"]:
                poly = h3.cell_to_boundary(z)
                poly_lonlat = [[p[1], p[0]] for p in poly] # JS turf needs lon,lat
                color = dynamic_zones[z]["color"]
                
                if not color: # fallback
                    color = "#FF0000" if dynamic_zones[z]["level"] in ["FATAL", "CRITICAL"] else "#FFA500"
                
                zones_data.append({
                    "polygon": poly_lonlat, 
                    "color": color,
                    "level": dynamic_zones[z]["level"],
                    "score": dynamic_zones[z]["score"]
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
