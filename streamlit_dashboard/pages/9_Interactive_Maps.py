"""
Interactive Geospatial Mapping
Shows campus locations and stall distribution
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

st.set_page_config(page_title="Interactive Maps", page_icon="🗺️", layout="wide")

st.title("🗺️ CampusEats Interactive Maps")

# Load data
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'campuseats.db')

@st.cache_data(ttl=3600)
def load_data():
    conn = sqlite3.connect(db_path)
    orders = pd.read_sql_query('SELECT * FROM orders', conn)
    students = pd.read_sql_query('SELECT * FROM students', conn)
    stalls = pd.read_sql_query('SELECT * FROM stalls', conn)
    universities = pd.read_sql_query('SELECT * FROM universities', conn)
    conn.close()
    return orders, students, stalls, universities

orders, students, stalls, universities = load_data()

# University coordinates
university_coords = {
    'NUST': {'lat': 33.6453, 'lon': 73.3604},
    'UET Lahore': {'lat': 31.5497, 'lon': 74.3436},
    'IBA Karachi': {'lat': 24.8407, 'lon': 67.0882}
}

# Tabs
tab1, tab2 = st.tabs(["🗺️ Campus Map", "📊 Campus Analytics"])

# ===== TAB 1: CAMPUS MAP =====
with tab1:
    st.subheader("University Locations")
    
    # Create data for map
    map_data = []
    for uni_id in universities['university_id'].values:
        uni_name = universities[universities['university_id'] == uni_id]['university_name'].values[0]
        coords = university_coords.get(uni_name, {'lat': 30.5, 'lon': 69.2})
        uni_orders = len(orders[orders['university_id'] == uni_id])
        uni_revenue = orders[orders['university_id'] == uni_id]['total_amount'].sum()
        
        map_data.append({
            'University': uni_name,
            'lat': coords['lat'],
            'lon': coords['lon'],
            'Orders': uni_orders,
            'Revenue': uni_revenue,
            'Size': uni_orders / 10
        })
    
    map_df = pd.DataFrame(map_data)
    
    # Create scatter map
    fig = px.scatter_mapbox(
        map_df,
        lat='lat',
        lon='lon',
        size='Size',
        color='Revenue',
        hover_name='University',
        hover_data={'Orders': True, 'Revenue': ':.0f', 'lat': False, 'lon': False, 'Size': False},
        title='Campus Locations',
        color_continuous_scale='Viridis',
        zoom=5,
        height=600
    )
    
    fig.update_layout(mapbox_style='open-street-map')
    fig.update_layout(margin={'r': 0, 't': 30, 'l': 0, 'b': 0})
    
    st.plotly_chart(fig, use_container_width=True)

# ===== TAB 2: CAMPUS ANALYTICS =====
with tab2:
    st.subheader("Campus Performance Comparison")
    
    campus_stats = []
    for uni_id in universities['university_id'].values:
        uni_name = universities[universities['university_id'] == uni_id]['university_name'].values[0]
        uni_orders = len(orders[orders['university_id'] == uni_id])
        uni_revenue = orders[orders['university_id'] == uni_id]['total_amount'].sum()
        uni_students = students[students['university_id'] == uni_id].shape[0]
        uni_stalls = len(stalls[stalls['university_id'] == uni_id])
        
        campus_stats.append({
            'University': uni_name,
            'Orders': uni_orders,
            'Revenue (PKR)': f"{uni_revenue:,.0f}",
            'Students': uni_students,
            'Stalls': uni_stalls,
            'Avg Order': f"{uni_revenue/uni_orders:.0f}" if uni_orders > 0 else "0"
        })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.dataframe(pd.DataFrame(campus_stats), use_container_width=True)
    
    with col2:
        # Bar chart
        chart_data = pd.DataFrame(campus_stats)
        chart_data['Revenue Numeric'] = orders.groupby('university_id')['total_amount'].sum().values
        
        fig = px.bar(chart_data, x='University', y='Revenue Numeric',
                    title='Revenue by Campus',
                    color='Revenue Numeric',
                    color_continuous_scale='Viridis',
                    labels={'Revenue Numeric': 'Revenue (PKR)'})
        st.plotly_chart(fig, use_container_width=True)
    
    st.info("📍 Maps show approximate campus locations. Stall locations are simulated within campus areas.")
