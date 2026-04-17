import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="CampusEats", page_icon="🍔", layout="wide")

st.title("🍔 CampusEats Analytics System")

st.markdown("""
## 🎉 Welcome to CampusEats!

This is a **demo version** of my capstone project.

### 📊 Features Available:

| Feature | Status |
|---------|--------|
| ML Predictions | ✅ |
| AI Chatbots | ✅ |
| Analytics Dashboard | ✅ |
| Interactive Maps | ✅ |
| Sentiment Analysis | ✅ |
| Gamification | ✅ |

### 🚀 Full Project:

- **GitHub:** [github.com/Hamasikram/CampusEats-Analytics-System](https://github.com/Hamasikram/CampusEats-Analytics-System)
- **Live Demo:** Limited due to cloud constraints

### 📈 Key Metrics (Sample Data):

""")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Revenue", "PKR 125,000")
with col2:
    st.metric("Total Orders", "150")
with col3:
    st.metric("Avg Order", "PKR 833")
with col4:
    st.metric("Active Students", "45")

st.info("💡 For full functionality including ML predictions, chatbots, and games, please run locally or check the GitHub repository.")

st.markdown("---")
st.markdown("### 🔗 Connect With Me")
st.markdown("- [GitHub](https://github.com/Hamasikram)")
st.markdown("- [LinkedIn](https://linkedin.com/in/hamasikram)")

st.caption("CampusEats Analytics System | Perfect Score 30/30 ⭐⭐⭐⭐⭐")
