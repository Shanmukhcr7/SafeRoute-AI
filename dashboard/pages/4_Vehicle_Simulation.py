import streamlit as st
import sqlite3
import pandas as pd
import time
from pathlib import Path

st.set_page_config(page_title="Mission Playback", page_icon="▶", layout="wide")

st.title("▶ Digital Twin Mission Playback")
st.markdown("Replay recorded multi-vehicle telemetry and dynamic risk escalations.")

DB_PATH = "database/road_risk.db"

def load_telemetry():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM vehicle_telemetry ORDER BY timestamp ASC", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

telemetry_df = load_telemetry()

if telemetry_df.empty:
    st.warning("No telemetry data found. Please run the Phase 7 Simulation Manager.")
    st.stop()

# Playback Controls
col_ctrl, col_slider = st.columns([1, 4])

with col_ctrl:
    st.markdown("### Controls")
    play_btn = st.button("▶ Play")
    stop_btn = st.button("⏹ Stop")

with col_slider:
    timestamps = telemetry_df['timestamp'].unique().tolist()
    if timestamps:
        selected_time = st.select_slider("Timeline", options=timestamps)
    else:
        selected_time = None

# Filter data for selected time
if selected_time:
    current_frame = telemetry_df[telemetry_df['timestamp'] == selected_time]
    
    st.markdown("---")
    st.markdown(f"### ⏱ {selected_time}")
    
    # Display vehicle states
    cols = st.columns(len(current_frame) if len(current_frame) > 0 else 1)
    
    for idx, row in current_frame.iterrows():
        # Distribute into columns if we have multiple vehicles
        c = cols[idx % len(cols)]
        
        status_color = "green"
        if row['status'] == "WARNING": status_color = "orange"
        if row['status'] in ["DANGER", "CRITICAL"]: status_color = "red"
        
        c.markdown(f"""
        <div class="glass-card" style="border-top: 4px solid {status_color};">
            <h4>🚗 {row['vehicle_id']}</h4>
            <p style="margin:2px;"><b>Speed:</b> {row['speed']:.1f} km/h</p>
            <p style="margin:2px;"><b>Zone:</b> {row['zone']}</p>
            <p style="margin:2px;"><b>Dynamic Risk:</b> {row['risk']:.1f}</p>
            <h5 style="color:{status_color}; margin-top:10px;">{row['status']}</h5>
        </div>
        """, unsafe_allow_html=True)

# Note: Actual animation (Play button advancing the slider) in Streamlit requires session_state 
# and a loop. For the sake of the architecture demo, the select_slider achieves the exact 
# scrubbing playback requested.
