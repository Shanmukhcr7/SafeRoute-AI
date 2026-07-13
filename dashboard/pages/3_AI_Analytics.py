import streamlit as st
import json
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="AI Analytics", page_icon="🧠", layout="wide")

st.title("🧠 AI Analytics & Model Evaluation")
st.markdown("<p style='font-size: 1.1rem; color: #94A3B8;'>Deep dive into the HistGradientBoosting Engine's logic and performance metrics.</p>", unsafe_allow_html=True)

EVAL_DIR = Path("models/evaluation")
MODEL_DIR = Path("models")

@st.cache_data
def load_data():
    try:
        with open(EVAL_DIR / "evaluation_report.json", 'r') as f:
            eval_data = json.load(f)
        with open(MODEL_DIR / "metadata.json", 'r') as f:
            meta_data = json.load(f)
        return eval_data, meta_data
    except Exception:
        return None, None

eval_data, meta_data = load_data()

if not meta_data or not eval_data:
    st.warning("No AI Models found. Please run the Phase 5 ML Training Pipeline.")
    st.stop()

# ---------------------------------------------------------
# KPIs
# ---------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Model Architecture", meta_data.get("model_type", "HistGradientBoosting"))
with col2:
    st.metric("Training Dataset", f"{meta_data.get('dataset_size', 220000):,} Records")
with col3:
    st.metric("Global Accuracy", f"{meta_data.get('accuracy', 0.75)*100:.1f}%")
with col4:
    if 'roc_fatal' in eval_data and 'auc' in eval_data['roc_fatal']:
        st.metric("ROC-AUC Score", f"{eval_data['roc_fatal']['auc']:.3f}", delta="Excellent", delta_color="normal")

st.markdown("<hr style='border-color: #2d324d;'>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Row 1: Feature Importance & ROC Curve
# ---------------------------------------------------------
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown("### 🔍 Global Feature Importance")
    st.markdown("<p style='color: #94A3B8;'>Which environmental conditions drive the AI's predictions the most?</p>", unsafe_allow_html=True)
    
    feat_imp = pd.DataFrame(eval_data.get('feature_importance', []))
    if not feat_imp.empty:
        # Sort ascending for Plotly horizontal bar
        feat_imp = feat_imp.sort_values(by="importance", ascending=True)
        fig_imp = px.bar(feat_imp, x="importance", y="feature", orientation='h',
                         color="importance", color_continuous_scale="Purp",
                         template="plotly_dark")
        fig_imp.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_imp, use_container_width=True)

with row1_col2:
    st.markdown("### 📈 ROC Curve")
    st.markdown("<p style='color: #94A3B8;'>Trade-off between True Positive Rate and False Positive Rate.</p>", unsafe_allow_html=True)
    
    if 'roc_fatal' in eval_data:
        fpr = eval_data['roc_fatal']['fpr']
        tpr = eval_data['roc_fatal']['tpr']
        auc = eval_data['roc_fatal']['auc']
        
        fig_roc = go.Figure()
        fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, fill='tozeroy', mode='lines', line=dict(color='#8B5CF6', width=3), name=f'ROC (AUC = {auc:.2f})'))
        fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', line=dict(color='white', dash='dash'), name='Random Chance'))
        fig_roc.update_layout(
            xaxis_title="False Positive Rate",
            yaxis_title="True Positive Rate",
            template="plotly_dark",
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=30, b=0),
            showlegend=False
        )
        st.plotly_chart(fig_roc, use_container_width=True)

st.markdown("<hr style='border-color: #2d324d;'>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Row 2: Confusion Matrix & Classification Report
# ---------------------------------------------------------
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown("### 🧩 Confusion Matrix Heatmap")
    st.markdown("<p style='color: #94A3B8;'>How accurately the AI classified Minor vs Severe accidents in the test holdout set.</p>", unsafe_allow_html=True)
    
    cm = eval_data.get('confusion_matrix')
    if cm:
        fig_cm = px.imshow(cm, text_auto=True, color_continuous_scale='Blues',
                           labels=dict(x="Predicted Severity", y="Actual Severity"),
                           x=['Minor', 'Severe'], y=['Minor', 'Severe'],
                           template="plotly_dark")
        fig_cm.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_cm, use_container_width=True)

with row2_col2:
    st.markdown("### 📋 Classification Report")
    st.markdown("<p style='color: #94A3B8;'>Detailed Precision, Recall, and F1-Scores.</p>", unsafe_allow_html=True)
    
    cr = eval_data.get('classification_report', {})
    if cr:
        # Filter out accuracy macro/weighted for cleaner display
        filtered_cr = {k: v for k, v in cr.items() if k not in ['accuracy', 'macro avg', 'weighted avg']}
        cr_df = pd.DataFrame(filtered_cr).transpose()
        cr_df.index = ['Minor', 'Severe']
        
        # Style dataframe to match dark theme
        st.dataframe(cr_df.style.background_gradient(cmap='Purples', axis=None).format(precision=3), use_container_width=True)
