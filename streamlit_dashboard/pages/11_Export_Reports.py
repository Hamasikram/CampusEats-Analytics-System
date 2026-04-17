"""
Export Reports & Data Analysis
Generate downloadable reports in multiple formats
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

st.set_page_config(page_title="Export Reports", page_icon="📄", layout="wide")

st.title("📄 Export Reports & Analytics")

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
    conn.close()
    
    if 'order_date' in orders.columns:
        orders['order_date'] = pd.to_datetime(orders['order_date'])
    
    return orders, students, stalls, universities, ratings, order_items

orders, students, stalls, universities, ratings, order_items = load_data()

# Get date range safely
if len(orders) > 0 and 'order_date' in orders.columns:
    min_date = orders['order_date'].min().date()
    max_date = orders['order_date'].max().date()
else:
    min_date = datetime.now().date()
    max_date = datetime.now().date()

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Executive Report", "📥 Data Export", "📈 Custom Report"])

# ===== TAB 1: EXECUTIVE REPORT =====
with tab1:
    st.subheader("Generate Executive Summary Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_format = st.selectbox("Report Format", ["Text", "Markdown"])
    
    with col2:
        include_details = st.checkbox("Include detailed metrics", value=True)
    
    if st.button("Generate Executive Report"):
        total_revenue = orders['total_amount'].sum() if len(orders) > 0 else 0
        total_orders = len(orders)
        avg_order = orders['total_amount'].mean() if len(orders) > 0 else 0
        unique_students = orders['student_id'].nunique() if len(orders) > 0 else 0
        avg_rating = ratings['rating'].mean() if len(ratings) > 0 else 0
        
        report = f"""
{'='*60}
CAMPUSEATS EXECUTIVE SUMMARY REPORT
{'='*60}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 KEY METRICS
{'='*40}
Total Revenue:        PKR {total_revenue:,.0f}
Total Orders:         {total_orders:,}
Average Order Value:  PKR {avg_order:,.0f}
Unique Students:      {unique_students:,}
Average Rating:       {avg_rating:.2f}⭐

📈 CAMPUS BREAKDOWN
{'='*40}
"""
        
        for uni_id in universities['university_id'].values:
            uni_name = universities[universities['university_id'] == uni_id]['university_name'].values[0]
            uni_revenue = orders[orders['university_id'] == uni_id]['total_amount'].sum() if len(orders) > 0 else 0
            uni_orders = len(orders[orders['university_id'] == uni_id]) if len(orders) > 0 else 0
            report += f"\n{uni_name}:\n"
            report += f"  Revenue: PKR {uni_revenue:,.0f}\n"
            report += f"  Orders: {uni_orders}\n"
        
        if include_details and len(stalls) > 0:
            report += f"\n🏪 TOP STALLS\n{'='*40}\n"
            if len(orders) > 0:
                top_stalls = orders.groupby('stall_id').size().nlargest(5)
                for stall_id, count in top_stalls.items():
                    stall_name = stalls[stalls['stall_id'] == stall_id]['stall_name'].values[0] if len(stalls[stalls['stall_id'] == stall_id]) > 0 else "Unknown"
                    revenue = orders[orders['stall_id'] == stall_id]['total_amount'].sum() if len(orders) > 0 else 0
                    report += f"{stall_name}: {count} orders, PKR {revenue:,.0f}\n"
        
        report += f"\n{'='*60}\nEnd of Report\n{'='*60}"
        
        if report_format == "Text":
            st.text(report)
        else:
            st.markdown(report)
        
        st.download_button(
            label="📥 Download Report",
            data=report,
            file_name=f"campus_eats_report_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

# ===== TAB 2: DATA EXPORT =====
with tab2:
    st.subheader("Export Raw Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Orders Data**")
        if st.button("Export Orders"):
            csv = orders.to_csv(index=False)
            st.download_button("Download CSV", csv, "orders.csv", "text/csv")
        
        st.write("**Students Data**")
        if st.button("Export Students"):
            csv = students.to_csv(index=False)
            st.download_button("Download CSV", csv, "students.csv", "text/csv")
        
        st.write("**Stalls Data**")
        if st.button("Export Stalls"):
            csv = stalls.to_csv(index=False)
            st.download_button("Download CSV", csv, "stalls.csv", "text/csv")
    
    with col2:
        st.write("**Ratings Data**")
        if st.button("Export Ratings"):
            csv = ratings.to_csv(index=False)
            st.download_button("Download CSV", csv, "ratings.csv", "text/csv")
        
        st.write("**Order Items Data**")
        if st.button("Export Order Items"):
            csv = order_items.to_csv(index=False)
            st.download_button("Download CSV", csv, "order_items.csv", "text/csv")
        
        st.write("**Universities Data**")
        if st.button("Export Universities"):
            csv = universities.to_csv(index=False)
            st.download_button("Download CSV", csv, "universities.csv", "text/csv")

# ===== TAB 3: CUSTOM REPORT =====
with tab3:
    st.subheader("Create Custom Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_campus = st.multiselect(
            "Select Campuses",
            options=universities['university_name'].tolist() if len(universities) > 0 else [],
            default=universities['university_name'].tolist() if len(universities) > 0 else []
        )
    
    with col2:
        if len(orders) > 0:
            date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date)
            )
        else:
            date_range = (datetime.now().date(), datetime.now().date())
            st.warning("No orders data available")
    
    if st.button("Generate Custom Report"):
        if len(orders) > 0:
            filtered_orders = orders.copy()
            
            if len(date_range) == 2:
                filtered_orders = filtered_orders[
                    (filtered_orders['order_date'].dt.date >= date_range[0]) &
                    (filtered_orders['order_date'].dt.date <= date_range[1])
                ]
            
            if selected_campus and len(universities) > 0:
                uni_ids = universities[universities['university_name'].isin(selected_campus)]['university_id'].tolist()
                filtered_orders = filtered_orders[filtered_orders['university_id'].isin(uni_ids)]
            
            date_range_text = f"{date_range[0]} to {date_range[1]}" if len(date_range) == 2 else "All time"
            campuses_text = ', '.join(selected_campus) if selected_campus else 'All'
            
            custom_report = f"""
CUSTOM REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Date Range: {date_range_text}
Campuses: {campuses_text}

SUMMARY STATISTICS
Total Revenue: PKR {filtered_orders['total_amount'].sum():,.0f}
Total Orders: {len(filtered_orders)}
Average Order: PKR {filtered_orders['total_amount'].mean():.0f if len(filtered_orders) > 0 else 0}
            """
            
            st.text(custom_report)
            
            st.download_button(
                label="Download Custom Report",
                data=custom_report,
                file_name=f"custom_report_{datetime.now().strftime('%Y%m%d')}.txt"
            )
            
            st.dataframe(filtered_orders.head(100), use_container_width=True)
        else:
            st.error("No orders data available")

st.success("✅ Export system ready! Generate reports and export data as needed.")
