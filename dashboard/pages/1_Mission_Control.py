import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

st.set_page_config(page_title="Mission Control", page_icon="📡", layout="wide")

st.title("📡 Mission Control Center")

DB_PATH = "database/road_risk.db"

def load_kpis():
    try:
        conn = sqlite3.connect(DB_PATH)
        # Mock KPIs if db is empty, else fetch actuals
        cursor = conn.cursor()
        
        # Alerts
        alerts_df = pd.read_sql_query("SELECT * FROM alerts ORDER BY time DESC LIMIT 50", conn)
        critical_alerts = len(alerts_df[alerts_df['type'] == 'CRITICAL'])
        
        # Telemetry
        telemetry_df = pd.read_sql_query("SELECT * FROM vehicle_telemetry ORDER BY timestamp DESC LIMIT 100", conn)
        active_vehicles = telemetry_df['vehicle_id'].nunique() if not telemetry_df.empty else 0
        avg_risk = telemetry_df['risk'].mean() if not telemetry_df.empty else 0.0
        
        conn.close()
        return alerts_df, active_vehicles, critical_alerts, avg_risk
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame(), 0, 0, 0.0

alerts_df, active_vehicles, critical_alerts, avg_risk = load_kpis()

# --- KPI Section ---
st.markdown("### System Status")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Active Digital Twins", value=active_vehicles)
with col2:
    st.metric(label="Average Dynamic Risk", value=f"{avg_risk:.1f}", delta="Stable" if avg_risk < 50 else "+High Risk", delta_color="inverse")
with col3:
    st.metric(label="Critical Alerts (24h)", value=critical_alerts)
with col4:
    st.metric(label="Current Weather", value="Rain", delta="Visibility -30%", delta_color="inverse")

st.markdown("---")

# --- Layout ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 📈 Recent Telemetry (Live)")
    if not alerts_df.empty:
        # Just show a chart of risks if telemetry exists
        try:
            conn = sqlite3.connect(DB_PATH)
            history = pd.read_sql_query("SELECT timestamp, risk FROM vehicle_telemetry ORDER BY timestamp DESC LIMIT 50", conn)
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            history = history.set_index('timestamp')
            st.line_chart(history['risk'])
            conn.close()
        except:
            st.info("No telemetry history available yet.")
    else:
        st.info("Simulation offline. No telemetry available.")

with col_right:
    st.markdown("### ⚠ Alert Center")
    if not alerts_df.empty:
        for _, row in alerts_df.head(5).iterrows():
            color = "red" if row['type'] == "CRITICAL" else "orange" if row['type'] == "DANGER" else "yellow"
            st.markdown(f"""
            <div style="border-left: 4px solid {color}; padding: 10px; margin-bottom: 10px; background-color: rgba(255,255,255,0.05); border-radius: 4px;">
                <b style="color:{color}">{row['type']} ALERT</b> - {row['time']}<br>
                <span style="font-size:0.9em; color:#ccc;">Vehicle: {row['vehicle']} | Zone: {row['zone']} | Risk: {row['risk']:.1f}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("No active alerts. System nominal.")
