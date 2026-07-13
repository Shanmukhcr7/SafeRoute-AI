import streamlit as st
import sqlite3
import pandas as pd
import folium
import streamlit.components.v1 as components
import h3

st.set_page_config(page_title="France Risk Zones", page_icon="🗺", layout="wide")

st.title("🇫🇷 National Risk Zone Database")
st.markdown("This map visualizes the historical H3 risk zones aggregated from the raw French accident dataset.")

@st.cache_data
def load_zones():
    conn = sqlite3.connect("database/road_risk.db")
    df = pd.read_sql_query("SELECT h3_index, risk_score, risk_level, risk_color FROM risk_scores WHERE risk_level IN ('CRITICAL', 'HIGH') LIMIT 5000", conn)
    conn.close()
    return df

df_zones = load_zones()

if df_zones.empty:
    st.warning("No high-risk zones found in the database. Ensure the initialization script ran successfully.")
else:
    st.metric("Total Critical & High Risk Zones Loaded", len(df_zones))
    
    # France center
    m = folium.Map(location=[46.2276, 2.2137], zoom_start=6, tiles="CartoDB positron")
    
    # For performance, we only draw the top critical ones if there are too many
    for _, row in df_zones.iterrows():
        poly = h3.cell_to_boundary(row['h3_index'])
        # folium expects (lat, lon) which h3 returns
        folium.Polygon(
            locations=poly,
            color=row['risk_color'],
            fill=True,
            fill_opacity=0.6,
            weight=1,
            tooltip=f"Risk Score: {row['risk_score']:.1f}"
        ).add_to(m)
        
    components.html(m._repr_html_(), height=800)
