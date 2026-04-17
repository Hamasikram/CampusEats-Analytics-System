"""
Advanced Histograms & Data Distributions
Most selling items, revenue patterns, customer behavior
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

st.set_page_config(page_title="Advanced Histograms", page_icon="📊", layout="wide")

st.title("📊 Advanced Histograms & Data Distributions")

# Load data
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'campuseats.db')

@st.cache_data(ttl=3600)
def load_data():
    conn = sqlite3.connect(db_path)
    orders = pd.read_sql_query('SELECT * FROM orders', conn)
    students = pd.read_sql_query('SELECT * FROM students', conn)
    stalls = pd.read_sql_query('SELECT * FROM stalls', conn)
    universities = pd.read_sql_query('SELECT * FROM universities', conn)
    ratings = pd.read_sql_query('SELECT * FROM ratings', conn)
    order_items = pd.read_sql_query('SELECT * FROM order_items', conn)
    categories = pd.read_sql_query('SELECT * FROM categories', conn)
    conn.close()
    
    if 'order_date' in orders.columns:
        orders['order_date'] = pd.to_datetime(orders['order_date'])
    return orders, students, stalls, universities, ratings, order_items, categories

orders, students, stalls, universities, ratings, order_items, categories = load_data()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🍕 Most Selling Items",
    "💰 Revenue Distribution",
    "👥 Customer Behavior",
    "⏰ Time Patterns"
])

# ===== TAB 1: MOST SELLING ITEMS =====
with tab1:
    st.subheader("🍕 Most Selling Food Items")
    
    if len(order_items) > 0:
        item_stats = order_items.groupby('item_name').agg({
            'quantity': 'sum',
            'item_total': 'sum'
        }).reset_index()
        item_stats.columns = ['Item', 'Total Quantity', 'Total Revenue']
        item_stats = item_stats.sort_values('Total Quantity', ascending=False).head(15)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(item_stats, x='Item', y='Total Quantity',
                        title='Top 15 Items by Quantity Sold',
                        color='Total Quantity',
                        color_continuous_scale='Blues')
            fig.update_layout(xaxis_tickangle=-45, height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(item_stats, x='Item', y='Total Revenue',
                        title='Top 15 Items by Revenue',
                        color='Total Revenue',
                        color_continuous_scale='Greens')
            fig.update_layout(xaxis_tickangle=-45, height=500)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No order items data available")

# ===== TAB 2: REVENUE DISTRIBUTION =====
with tab2:
    st.subheader("💰 Revenue Distribution Analysis")
    
    if len(orders) > 0:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Revenue", f"PKR {orders['total_amount'].sum():,.0f}")
        with col2:
            st.metric("Average Order", f"PKR {orders['total_amount'].mean():.0f}")
        with col3:
            st.metric("Median Order", f"PKR {orders['total_amount'].median():.0f}")
        with col4:
            st.metric("Std Deviation", f"PKR {orders['total_amount'].std():.0f}")
        
        fig = px.histogram(orders, x='total_amount', nbins=30,
                          title='Order Value Distribution',
                          color_discrete_sequence=['#FF6B6B'],
                          labels={'total_amount': 'Order Value (PKR)'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No orders data available")

# ===== TAB 3: CUSTOMER BEHAVIOR =====
with tab3:
    st.subheader("👥 Customer Behavior Analysis")
    
    if len(orders) > 0 and len(students) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            orders_per_student = orders.groupby('student_id').size().reset_index(name='orders')
            fig = px.histogram(orders_per_student, x='orders', nbins=20,
                              title='Orders per Student',
                              color_discrete_sequence=['#4ECDC4'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.histogram(students, x='total_spending', nbins=20,
                              title='Student Spending Distribution',
                              color_discrete_sequence=['#95A5A6'])
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No customer data available")

# ===== TAB 4: TIME PATTERNS =====
with tab4:
    st.subheader("⏰ Time-based Patterns")
    
    if len(orders) > 0:
        orders_copy = orders.copy()
        orders_copy['hour'] = orders_copy['order_date'].dt.hour
        hourly = orders_copy.groupby('hour').size().reset_index(name='count')
        
        fig = px.bar(hourly, x='hour', y='count',
                    title='Orders by Hour of Day',
                    color='count',
                    color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No time data available")

st.info("📊 Advanced histograms showing item popularity, revenue distribution, customer behavior, and time patterns")
