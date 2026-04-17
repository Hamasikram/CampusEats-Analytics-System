"""
Comparative Dashboard
Compare stalls, categories, universities side-by-side
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

st.set_page_config(page_title="Comparative Dashboard", page_icon="⚖️", layout="wide")

st.title("⚖️ Comparative Analysis Dashboard")

# Load data
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'campuseats.db')

@st.cache_data(ttl=3600)
def load_data():
    conn = sqlite3.connect(db_path)
    orders = pd.read_sql_query('SELECT * FROM orders', conn)
    stalls = pd.read_sql_query('SELECT * FROM stalls', conn)
    universities = pd.read_sql_query('SELECT * FROM universities', conn)
    ratings = pd.read_sql_query('SELECT * FROM ratings', conn)
    categories = pd.read_sql_query('SELECT * FROM categories', conn)
    conn.close()
    
    if 'order_date' in orders.columns:
        orders['order_date'] = pd.to_datetime(orders['order_date'])
    return orders, stalls, universities, ratings, categories

orders, stalls, universities, ratings, categories = load_data()

# Tabs
tab1, tab2, tab3 = st.tabs([
    "🏪 Stall Comparison",
    "🏫 University Comparison",
    "📁 Category Comparison"
])

# ===== TAB 1: STALL COMPARISON =====
with tab1:
    st.subheader("🏪 Compare Stalls")
    
    if len(stalls) > 0:
        stall_names = stalls['stall_name'].tolist()
        default_stalls = stall_names[:3] if len(stall_names) >= 3 else stall_names
        
        selected_stalls = st.multiselect(
            "Select Stalls to Compare",
            stall_names,
            default=default_stalls
        )
        
        if selected_stalls and len(orders) > 0:
            stall_ids = stalls[stalls['stall_name'].isin(selected_stalls)]['stall_id'].tolist()
            
            comparison_data = []
            for stall_id in stall_ids:
                stall_name = stalls[stalls['stall_id'] == stall_id]['stall_name'].values[0]
                stall_orders = orders[orders['stall_id'] == stall_id]
                stall_ratings = ratings[ratings['stall_id'] == stall_id]
                
                comparison_data.append({
                    'Stall': stall_name,
                    'Orders': len(stall_orders),
                    'Revenue': stall_orders['total_amount'].sum(),
                    'Avg Rating': stall_ratings['rating'].mean() if len(stall_ratings) > 0 else 0
                })
            
            comp_df = pd.DataFrame(comparison_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(comp_df, x='Stall', y='Orders',
                            title='Orders Comparison',
                            color='Orders',
                            color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(comp_df, x='Stall', y='Revenue',
                            title='Revenue Comparison (PKR)',
                            color='Revenue',
                            color_continuous_scale='Greens')
                st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(comp_df, use_container_width=True)
        else:
            st.info("Select stalls to compare")
    else:
        st.info("No stall data available")

# ===== TAB 2: UNIVERSITY COMPARISON =====
with tab2:
    st.subheader("🏫 Compare Universities")
    
    if len(universities) > 0 and len(orders) > 0:
        uni_comparison = []
        for uni_id in universities['university_id'].values:
            uni_name = universities[universities['university_id'] == uni_id]['university_name'].values[0]
            uni_orders = orders[orders['university_id'] == uni_id]
            
            uni_comparison.append({
                'University': uni_name,
                'Orders': len(uni_orders),
                'Revenue': uni_orders['total_amount'].sum(),
                'Avg Order': uni_orders['total_amount'].mean() if len(uni_orders) > 0 else 0
            })
        
        uni_df = pd.DataFrame(uni_comparison)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(uni_df, x='University', y='Revenue',
                        title='Revenue by University',
                        color='Revenue',
                        color_continuous_scale='Plasma')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.pie(values=uni_df['Revenue'], names=uni_df['University'],
                        title='Revenue Share')
            st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(uni_df, use_container_width=True)
    else:
        st.info("No university data available")

# ===== TAB 3: CATEGORY COMPARISON =====
with tab3:
    st.subheader("📁 Compare Food Categories")
    
    if len(categories) > 0 and len(stalls) > 0 and len(orders) > 0:
        cat_comparison = []
        for cat_id in categories['category_id'].values:
            cat_name = categories[categories['category_id'] == cat_id]['category_name'].values[0]
            cat_stalls = stalls[stalls['category_id'] == cat_id]['stall_id'].tolist()
            cat_orders = orders[orders['stall_id'].isin(cat_stalls)]
            cat_ratings = ratings[ratings['stall_id'].isin(cat_stalls)]
            
            cat_comparison.append({
                'Category': cat_name,
                'Orders': len(cat_orders),
                'Revenue': cat_orders['total_amount'].sum(),
                'Avg Rating': cat_ratings['rating'].mean() if len(cat_ratings) > 0 else 0,
                'Stalls': len(cat_stalls)
            })
        
        cat_df = pd.DataFrame(cat_comparison)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(cat_df, x='Category', y='Revenue',
                        title='Revenue by Category',
                        color='Revenue',
                        color_continuous_scale='Turbo')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(cat_df, x='Category', y='Avg Rating',
                        title='Average Rating by Category',
                        color='Avg Rating',
                        color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(cat_df, use_container_width=True)
    else:
        st.info("No category data available")

st.info("⚖️ Compare performance across stalls, universities, and food categories")
