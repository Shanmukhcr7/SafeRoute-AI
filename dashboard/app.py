import streamlit as st
import sys
from pathlib import Path

# Add project root to path so we can import our modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Global Page Config
st.set_page_config(
    page_title="AI Road Traffic Command Center",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global CSS removed in favor of .streamlit/config.toml light theme

st.title("🚦 AI Road Traffic Intelligence Command Center")

st.markdown("""
<div class="glass-card">
    <h3>Welcome to the Mission Control System</h3>
    <p>Select a module from the sidebar to begin monitoring the intelligent transportation network.</p>
    <ul>
        <li><b>Mission Control:</b> High-level KPIs and Alert streams.</li>
        <li><b>Live Map:</b> Interactive GIS Engine and Scenario Simulator.</li>
        <li><b>AI Analytics:</b> Deep dive into the AI Severity predictions and SHAP explanations.</li>
        <li><b>Digital Twin Simulation:</b> Control and playback multi-vehicle simulations.</li>
        <li><b>System Health:</b> Enterprise monitoring of the architecture.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.info("System Initialized. All engines online.")
