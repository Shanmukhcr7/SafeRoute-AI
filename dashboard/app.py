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
    /* Main Background - Deep Premium Dark */
    .stApp {
        background-color: #0f111a;
        color: #E2E8F0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1d2d !important;
        border-right: 1px solid #2d324d;
    }
    
    /* Metrics / KPI Cards */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #3B82F6 !important; /* Beautiful Blue */
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        color: #94A3B8 !important;
    }
    
    /* Premium Glassmorphism Containers */
    .glass-card {
        background: linear-gradient(145deg, rgba(30, 34, 53, 0.7), rgba(20, 23, 38, 0.4));
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        padding: 30px;
        margin-bottom: 25px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4);
    }
    
    /* Titles and Typography */
    h1 {
        font-weight: 800 !important;
        background: -webkit-linear-gradient(45deg, #3B82F6, #8B5CF6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        margin-bottom: 30px !important;
    }
    h2, h3 {
        color: #F8FAFC !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px;
    }
    p, li {
        font-size: 1.05rem;
        line-height: 1.7;
        color: #CBD5E1;
    }
    
    /* Highlights */
    .highlight-blue { color: #60A5FA; font-weight: 600; }
    .highlight-purple { color: #A78BFA; font-weight: 600; }
    .highlight-red { color: #F87171; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

st.title("🚦 AI Road Traffic Intelligence")

st.markdown("""
<div class="glass-card">
    <h2 style="margin-top:0;">The Mission</h2>
    <p>Welcome to the <b>Advanced Driver Assistance System (ADAS)</b> Dashboard. This platform was engineered to proactively prevent road accidents by combining <b>authentic historical police data</b>, high-resolution <b>spatial grid systems</b>, and a powerful <b>Machine Learning risk engine</b>.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="glass-card" style="height: 380px;">
        <h3>📊 The Dataset</h3>
        <p>This AI was trained on a massive, authentic government dataset containing <b>over 15 years</b> of traffic accident history.</p>
        <ul>
            <li><span class="highlight-blue">220,573</span> unique accident records analyzed.</li>
            <li>Contains high-fidelity coordinates mapped across the entire country of France.</li>
            <li>Records detailed environmental variables including <i>Lighting, Weather, Surface Conditions, and Time of Day</i>.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="glass-card" style="height: 380px;">
        <h3>🧠 The Architecture</h3>
        <p>We process millions of data points into actionable real-time intelligence using cutting-edge technologies.</p>
        <ul>
            <li><b>Uber H3 Grid System:</b> The globe is divided into standardized, highly-efficient hexagonal zones (Resolution 8) to map density and historical blackspots.</li>
            <li><b>HistGradientBoosting AI:</b> A state-of-the-art Machine Learning classifier capable of predicting the probability of a fatal crash under specific environmental conditions in milliseconds.</li>
            <li><b>Dynamic Risk Multipliers:</b> Intersections are dynamically recalculated on the fly based on current weather and lighting.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="glass-card">
    <h3 style="margin-top:0;">🚀 How to Use This Dashboard</h3>
    <p>Navigate using the sidebar on the left to explore the different modules of the system:</p>
    <ol>
        <li><b>1. France Risk Map:</b> View the Top 300 most dangerous intersections natively mapped in 3D across the entire country.</li>
        <li><b>2. Live Map:</b> Enter the Environment Simulator. Start a driving journey from Paris to Lyon and watch the AI dynamically adjust risk scores as you simulate Rain, Fog, or Nighttime driving!</li>
        <li><b>3. AI Analytics:</b> Deep dive into the mathematical evaluation of the Machine Learning Model to understand exactly how the AI "thinks" and makes its decisions.</li>
    </ol>
</div>
""", unsafe_allow_html=True)
