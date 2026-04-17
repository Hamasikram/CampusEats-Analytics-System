"""
Performance Metrics & KPIs
Advanced metrics and performance indicators
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.graph_objects as go
import plotly.express as px
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

st.set_page_config(page_title="Performance Metrics", page_icon="📊", layout="wide")

st.title("📊 Advanced Performance Metrics & KPIs")

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
    conn.close()
    
    if 'order_date' in orders.columns:
        orders['order_date'] = pd.to_datetime(orders['order_date'])
    return orders, students, stalls, universities, ratings

orders, students, stalls, universities, ratings = load_data()

# Tabs
tab1, tab2 = st.tabs([
    "🎯 Core KPIs",
    "📈 Growth Metrics"
])

# ===== TAB 1: CORE KPIs =====
with tab1:
    st.subheader("🎯 Core Performance Indicators")
    
    if len(orders) > 0 and len(students) > 0:
        total_revenue = orders['total_amount'].sum()
        total_orders = len(orders)
        avg_order_value = orders['total_amount'].mean()
        total_students = len(students)
        active_students = orders['student_id'].nunique()
        avg_rating = ratings['rating'].mean() if len(ratings) > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Total Revenue", f"PKR {total_revenue:,.0f}")
        with col2:
            st.metric("📦 Total Orders", f"{total_orders:,}")
        with col3:
            st.metric("💵 Avg Order", f"PKR {avg_order_value:.0f}")
        with col4:
            st.metric("👥 Total Students", f"{total_students:,}")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            active_pct = (active_students / total_students * 100)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=active_pct,
                title={'text': "Active Students (%)"},
                gauge={'axis': {'range': [0, 100]},
                       'bar': {'color': "#4ECDC4"},
                       'steps': [
                           {'range': [0, 30], 'color': "#FFE5E5"},
                           {'range': [30, 60], 'color': "#FFD9D9"},
                           {'range': [60, 100], 'color': "#90EE90"}
                       ]}
            ))
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=avg_rating,
                title={'text': "Average Rating"},
                gauge={'axis': {'range': [0, 5]},
                       'bar': {'color': "#FF6B6B"},
                       'steps': [
                           {'range': [0, 2], 'color': "#FFE5E5"},
                           {'range': [2, 3.5], 'color': "#FFD9D9"},
                           {'range': [3.5, 5], 'color': "#90EE90"}
                       ]}
            ))
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            orders_per_student = total_orders / total_students
            fig = go.Figure(go.Indicator(
                mode="number",
                value=orders_per_student,
                title={'text': "Orders per Student"}
            ))
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance scorecard
        st.markdown("---")
        st.subheader("📊 Performance Scorecard")
        
        metrics = {
            'Student Engagement': (active_students / total_students * 100),
            'Order Frequency': orders_per_student,
            'Customer LTV': total_revenue / total_students,
            'Avg Rating Score': avg_rating * 20
        }
        
        for metric, value in metrics.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{metric}**")
                if metric == 'Customer LTV':
                    st.write(f"PKR {value:,.0f}")
                else:
                    st.progress(min(value / 100, 1.0) if metric != 'Order Frequency' else min(value / 5, 1.0))
            with col2:
                if metric == 'Customer LTV':
                    st.write(f"PKR {value:,.0f}")
                elif metric == 'Order Frequency':
                    st.write(f"{value:.2f} orders/student")
                else:
                    st.write(f"{value:.1f}%")
    else:
        st.info("No data available for metrics")

# ===== TAB 2: GROWTH METRICS =====
with tab2:
    st.subheader("📈 Growth & Trend Analysis")
    
    if len(orders) > 0:
        orders_copy = orders.copy()
        orders_copy['date'] = orders_copy['order_date'].dt.date
        
        daily_data = orders_copy.groupby('date').agg({
            'order_id': 'count',
            'total_amount': 'sum'
        }).reset_index()
        daily_data.columns = ['date', 'orders', 'revenue']
        daily_data['cumulative_orders'] = daily_data['orders'].cumsum()
        daily_data['cumulative_revenue'] = daily_data['revenue'].cumsum()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(daily_data, x='date', y='cumulative_orders', markers=True,
                         title='Cumulative Orders Growth',
                         labels={'date': 'Date', 'cumulative_orders': 'Total Orders'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.line(daily_data, x='date', y='cumulative_revenue', markers=True,
                         title='Cumulative Revenue Growth',
                         labels={'date': 'Date', 'cumulative_revenue': 'Revenue (PKR)'})
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Daily average
        col1, col2 = st.columns(2)
        
        with col1:
            avg_daily_orders = daily_data['orders'].mean()
            st.metric("📊 Avg Daily Orders", f"{avg_daily_orders:.1f}")
        
        with col2:
            avg_daily_revenue = daily_data['revenue'].mean()
            st.metric("💰 Avg Daily Revenue", f"PKR {avg_daily_revenue:,.0f}")
    else:
        st.info("No order data available for growth metrics")

st.success("✅ Advanced performance metrics dashboard ready!")
