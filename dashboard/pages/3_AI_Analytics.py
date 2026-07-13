import streamlit as st
import json
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="AI Analytics", page_icon="🧠", layout="wide")

st.title("🧠 AI Analytics & Model Registry")

EVAL_DIR = Path("models/evaluation")
MODEL_DIR = Path("models")

def load_evaluation():
    try:
        with open(EVAL_DIR / "evaluation_report.json", 'r') as f:
            return json.load(f)
    except:
        return None

def load_metadata():
    try:
        with open(MODEL_DIR / "metadata.json", 'r') as f:
            return json.load(f)
    except:
        return None

eval_data = load_evaluation()
meta_data = load_metadata()

if not meta_data or not eval_data:
    st.warning("No AI Models found. Please run the Phase 5 ML Training Pipeline.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏆 Champion Model Metadata")
    st.json(meta_data)
    
    st.markdown("### 📊 Classification Report")
    cr_df = pd.DataFrame(eval_data['classification_report']).transpose()
    st.dataframe(cr_df.style.background_gradient(cmap='Blues'))

with col2:
    st.markdown("### 🔍 Global Feature Importance")
    st.info("What features drive the Severity prediction the most across the entire dataset?")
    
    feat_imp = pd.DataFrame(eval_data['feature_importance'])
    if not feat_imp.empty:
        st.bar_chart(feat_imp.set_index('feature'))
    else:
        st.write("Feature importance not available for this model type.")
        
st.markdown("---")
st.markdown("### 📉 ROC Curve / Confusion Matrix Metrics")
st.write("Confusion Matrix (Raw):", eval_data.get('confusion_matrix', []))
if 'roc_fatal' in eval_data and 'auc' in eval_data['roc_fatal']:
    st.metric(label="ROC-AUC (Fatal vs Rest)", value=f"{eval_data['roc_fatal']['auc']:.3f}")
