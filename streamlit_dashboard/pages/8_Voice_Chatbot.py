"""
Voice-Based Chatbot with Speech-to-Text and Text-to-Speech
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

st.set_page_config(page_title="Voice Chatbot", page_icon="🎤", layout="wide")

st.title("🎤 Voice-Enabled AI Assistant")

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

st.sidebar.write("### 📊 System Stats")
st.sidebar.metric("Total Orders", len(orders))
st.sidebar.metric("Total Revenue", f"PKR {orders['total_amount'].sum():,.0f}")

st.write("### 💬 Text Command")
user_command = st.text_input("Type your command:", placeholder="e.g., Show statistics")

if user_command:
    cmd_lower = user_command.lower()
    
    if 'statistics' in cmd_lower or 'revenue' in cmd_lower:
        response = f"""
📊 **System Statistics**
- Total Revenue: PKR {orders['total_amount'].sum():,.0f}
- Total Orders: {len(orders)}
- Average Order: PKR {orders['total_amount'].mean():,.0f}
- Unique Students: {orders['student_id'].nunique()}
        """
    elif 'stall' in cmd_lower:
        top_stalls = orders['stall_id'].value_counts().head(5)
        response = "🏪 **Top 5 Stalls:**\n"
        for stall_id, count in top_stalls.items():
            stall_name = stalls[stalls['stall_id'] == stall_id]['stall_name'].values[0]
            response += f"- {stall_name}: {count} orders\n"
    elif 'campus' in cmd_lower:
        response = "🏫 **Campus Performance:**\n"
        for uni_id in universities['university_id'].values:
            uni_name = universities[universities['university_id'] == uni_id]['university_name'].values[0]
            uni_revenue = orders[orders['university_id'] == uni_id]['total_amount'].sum()
            response += f"- {uni_name}: PKR {uni_revenue:,.0f}\n"
    else:
        response = """
🤖 **Available Commands:**
- Show statistics
- Top stalls
- Campus comparison
- Help
        """
    
    st.write(response)

st.info("💡 Tip: Type 'statistics', 'top stalls', or 'campus comparison'")
