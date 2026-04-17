"""
CampusEats Analytics & Prediction Dashboard
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Add parent directory to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Page Configuration
st.set_page_config(
    page_title="CampusEats Analytics",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { padding: 0px; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .section-header {
        font-size: 24px;
        font-weight: bold;
        margin: 20px 0 10px 0;
        border-bottom: 3px solid #FF6B6B;
        padding-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Database path
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'campuseats.db')

# ========== DATABASE FUNCTIONS ==========
@st.cache_resource
def get_db_connection():
    return sqlite3.connect(db_path)

def fetch_data(query, params=None):
    try:
        conn = get_db_connection()
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

# ========== LOAD DATA ==========
@st.cache_data(ttl=3600)
def load_all_data():
    conn = sqlite3.connect(db_path)
    
    orders = pd.read_sql_query('SELECT * FROM orders', conn)
    students = pd.read_sql_query('SELECT * FROM students', conn)
    stalls = pd.read_sql_query('SELECT * FROM stalls', conn)
    universities = pd.read_sql_query('SELECT * FROM universities', conn)
    ratings = pd.read_sql_query('SELECT * FROM ratings', conn)
    order_items = pd.read_sql_query('SELECT * FROM order_items', conn)
    categories = pd.read_sql_query('SELECT * FROM categories', conn)
    
    conn.close()
    
    return {
        'orders': orders,
        'students': students,
        'stalls': stalls,
        'universities': universities,
        'ratings': ratings,
        'order_items': order_items,
        'categories': categories
    }

data = load_all_data()
orders = data['orders']
students = data['students']
stalls = data['stalls']
universities = data['universities']
ratings = data['ratings']
order_items = data['order_items']
categories = data['categories']

# Convert dates
orders['order_date'] = pd.to_datetime(orders['order_date'])

# ========== SIDEBAR FILTERS ==========
st.sidebar.title("🎛️ Dashboard Filters")

selected_universities = st.sidebar.multiselect(
    "Select Universities",
    options=universities['university_name'].unique(),
    default=universities['university_name'].unique()
)

# Date Range Filter
min_date = orders['order_date'].min().date()
max_date = orders['order_date'].max().date()

col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("Start Date", min_date)
with col2:
    end_date = st.date_input("End Date", max_date)

# Filter data
filtered_orders = orders[
    (orders['order_date'].dt.date >= start_date) &
    (orders['order_date'].dt.date <= end_date) &
    (orders['university_id'].isin(universities[universities['university_name'].isin(selected_universities)]['university_id']))
].copy()

# ========== MAIN DASHBOARD ==========
st.title("🍔 CampusEats Analytics & Prediction System")

# ===== KPI CARDS =====
st.markdown('<div class="section-header">📊 Key Performance Indicators</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_revenue = filtered_orders['total_amount'].sum()
    st.metric("💰 Total Revenue", f"PKR {total_revenue:,.0f}")

with col2:
    total_orders = len(filtered_orders)
    st.metric("📦 Total Orders", f"{total_orders:,}")

with col3:
    avg_order_value = filtered_orders['total_amount'].mean() if total_orders > 0 else 0
    st.metric("💵 Avg Order Value", f"PKR {avg_order_value:,.0f}")

with col4:
    unique_students = filtered_orders['student_id'].nunique()
    st.metric("👥 Unique Students", f"{unique_students:,}")

# ===== CHARTS =====
st.markdown('<div class="section-header">📈 Sales Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    daily_sales = filtered_orders.groupby(filtered_orders['order_date'].dt.date).agg({
        'total_amount': 'sum'
    }).reset_index()
    daily_sales.columns = ['Date', 'Revenue']
    
    fig_sales = px.line(daily_sales, x='Date', y='Revenue', 
                        title='Daily Revenue Trend',
                        markers=True)
    st.plotly_chart(fig_sales, use_container_width=True)

with col2:
    hourly_orders = filtered_orders.copy()
    hourly_orders['hour'] = hourly_orders['order_date'].dt.hour
    hourly_counts = hourly_orders.groupby('hour').size().reset_index(name='count')
    
    fig_heatmap = px.bar(hourly_counts, x='hour', y='count',
                         title='Orders by Hour',
                         color='count',
                         color_continuous_scale='Viridis')
    st.plotly_chart(fig_heatmap, use_container_width=True)

# ===== REVENUE BY CAMPUS =====
st.markdown('<div class="section-header">🏫 Revenue by Campus</div>', unsafe_allow_html=True)

campus_revenue = filtered_orders.merge(universities, left_on='university_id', right_on='university_id')
campus_revenue = campus_revenue.groupby('university_name')['total_amount'].sum().reset_index()

fig_campus = px.pie(campus_revenue, values='total_amount', names='university_name',
                    title='Revenue Distribution by Campus',
                    color_discrete_sequence=px.colors.qualitative.Pastel)
st.plotly_chart(fig_campus, use_container_width=True)

st.info("📌 Use the sidebar to filter by university and date range. Navigate to other pages using the sidebar menu for Predictions and Analytics!")
