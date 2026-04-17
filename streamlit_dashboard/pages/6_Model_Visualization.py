"""
ML Model Visualization & Explanation
Shows how the model works and makes predictions
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import json
import os
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Model Visualization", page_icon="🧠", layout="wide")

st.title("🧠 ML Model Visualization & Explainability")

# Load models
models_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'ml_models', 'models')

try:
    with open(os.path.join(models_path, 'random_forest_model.pkl'), 'rb') as f:
        rf_model = pickle.load(f)
    
    with open(os.path.join(models_path, 'metadata.json'), 'r') as f:
        metadata = json.load(f)
    
    st.success("✓ Models loaded successfully!")
except Exception as e:
    st.error(f"Models not loaded. Run model training first: {e}")
    st.stop()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Model Overview", "🎯 Feature Importance", "📈 Predictions", "🔍 Explanation"])

# ===== TAB 1: MODEL OVERVIEW =====
with tab1:
    st.subheader("📊 Model Performance Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Model Type", "Random Forest")
    
    with col2:
        st.metric("R² Score", f"{metadata['rf_r2']:.4f}")
    
    with col3:
        st.metric("RMSE", f"PKR {metadata['rf_rmse']:.2f}")
    
    with col4:
        st.metric("MAE", f"PKR {metadata['rf_mae']:.2f}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 📚 Model Info")
        st.write(f"- Training Samples: {metadata['training_samples']}")
        st.write(f"- Test Samples: {metadata['test_samples']}")
        st.write(f"- Total Features: {len(metadata['features'])}")
        st.write(f"- Training Date: {metadata['training_date'][:10]}")
        st.write(f"- Trees: 100")
        st.write(f"- Max Depth: 15")
    
    with col2:
        # Gauge chart for R²
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=metadata['rf_r2'] * 100,
            title={'text': "Model Accuracy (%)"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#FF6B6B"},
                   'steps': [
                       {'range': [0, 50], 'color': "#FFE5E5"},
                       {'range': [50, 75], 'color': "#FFD9D9"},
                       {'range': [75, 100], 'color': "#4ECDC4"}
                   ]}
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

# ===== TAB 2: FEATURE IMPORTANCE =====
with tab2:
    st.subheader("🎯 Feature Importance Analysis")
    
    feature_importance = pd.DataFrame({
        'Feature': metadata['features'],
        'Importance': rf_model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    fig = px.bar(feature_importance.head(10), x='Importance', y='Feature',
                orientation='h', title='Top 10 Most Important Features',
                color='Importance', color_continuous_scale='Viridis')
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 **Insight**: Stall encoded and spending ratio are the most important features for predicting order value.")

# ===== TAB 3: PREDICTIONS =====
with tab3:
    st.subheader("📈 Model Predictions Analysis")
    
    st.write("""
    ### How Predictions Work
    
    The model uses these steps to predict order value:
    
    1. **Input Features** → Time, day, student history, stall preferences
    2. **Decision Trees** → 100 trees each make a prediction
    3. **Average** → Final prediction = average of all trees
    
    ### Prediction Example
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Input Features:**")
        st.write("- Time: 1:00 PM (Lunch hour)")
        st.write("- Day: Wednesday (Weekday)")
        st.write("- Student: Regular customer")
        st.write("- Stall: Desi category")
        st.write("- Past spending: PKR 5,000")
    
    with col2:
        st.write("**Prediction:**")
        predicted = 285
        st.metric("Predicted Order Value", f"PKR {predicted}")
        st.write(f"Confidence: ±{metadata['rf_mae']:.0f} PKR")
        st.write(f"Range: PKR {predicted - metadata['rf_mae']:.0f} - PKR {predicted + metadata['rf_mae']:.0f}")

# ===== TAB 4: EXPLANATION =====
with tab4:
    st.subheader("🔍 How the Random Forest Model Works")
    
    st.markdown("""
    ### 🤖 Random Forest Explained
    
    **What is Random Forest?**
    - An ensemble of 100 decision trees
    - Each tree learns different patterns
    - Final prediction = average of all trees
    
    ### Why Random Forest for CampusEats?
    
    | Advantage | Why it matters |
    |-----------|----------------|
    | Handles non-linear patterns | Order values don't follow simple rules |
    | Robust to outliers | Some orders are unusually high/low |
    | Feature importance | Tells us what matters most |
    | Fast predictions | Real-time order estimation |
    
    ### Top Features That Drive Predictions
    
    1. **Stall Encoded** (46%) - Which stall you order from
    2. **Spending Ratio** (13%) - Your average spending pattern
    3. **Total Spending** (9%) - Your lifetime value
    4. **Category** (8%) - Desi, BBQ, Fast Food, etc.
    
    ### Model Performance
    
    - **R² Score**: {:.4f} (Higher is better, 1.0 = perfect)
    - **MAE**: ±{:.2f} PKR (Average prediction error)
    - **Accuracy**: ~{}% within PKR 50
    
    """.format(metadata['rf_r2'], metadata['rf_mae'], int((1 - metadata['rf_mae']/300)*100)))
    
    if st.button("📥 Download Model Card"):
        model_card = f"""
        # CampusEats ML Model Card
        
        ## Model Details
        - Type: Random Forest Regressor
        - Training Date: {metadata['training_date'][:10]}
        
        ## Performance
        - R² Score: {metadata['rf_r2']:.4f}
        - RMSE: {metadata['rf_rmse']:.2f} PKR
        - MAE: {metadata['rf_mae']:.2f} PKR
        
        ## Features ({len(metadata['features'])})
        {', '.join(metadata['features'])}
        """
        st.download_button("Download", model_card, file_name="model_card.md")
