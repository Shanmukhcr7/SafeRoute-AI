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

# Custom Dark Theme & Glassmorphism CSS
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #0B1220;
        color: #E5E7EB;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        border-right: 1px solid #1F2937;
    }
    
    /* Metrics / KPI Cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        color: #3B82F6 !important; /* Blue Accent */
    }
    
    /* Glassmorphism Containers */
    .glass-card {
        background: rgba(17, 24, 39, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* Titles */
    h1, h2, h3 {
        color: #F9FAFB !important;
        font-weight: 600 !important;
    }
    
    /* Success/Warning/Critical Colors */
    .text-success { color: #10B981; }
    .text-warning { color: #F59E0B; }
    .text-critical { color: #EF4444; }
    .text-accent { color: #3B82F6; }
    </style>
""", unsafe_allow_html=True)

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
