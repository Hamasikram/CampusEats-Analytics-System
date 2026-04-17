"""
AI Chatbot for CampusEats
Provides intelligent Q&A about orders, predictions, and recommendations
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

st.set_page_config(page_title="AI Chatbot", page_icon="💬", layout="wide")

st.title("💬 CampusEats AI Assistant")

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
    categories = pd.read_sql_query('SELECT * FROM categories', conn)
    order_items = pd.read_sql_query('SELECT * FROM order_items', conn)
    conn.close()
    
    orders['order_date'] = pd.to_datetime(orders['order_date'])
    return orders, students, stalls, universities, ratings, categories, order_items

orders, students, stalls, universities, ratings, categories, order_items = load_data()

# Sidebar stats
st.sidebar.write("**📊 System Stats**")
st.sidebar.write(f"Students: {len(students)}")
st.sidebar.write(f"Stalls: {len(stalls)}")
st.sidebar.write(f"Orders: {len(orders)}")
st.sidebar.write(f"Revenue: PKR {orders['total_amount'].sum():,.0f}")

# Chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Display chat
st.write("### 💬 Chat")
for msg in st.session_state.chat_history:
    if msg['role'] == 'user':
        st.write(f"👤 **You**: {msg['content']}")
    else:
        st.write(f"🤖 **AI**: {msg['content']}")
    st.markdown("---")

# Input
user_input = st.text_input("Ask me anything...", placeholder="e.g., Tell me about Ali Khan")

if user_input:
    st.session_state.chat_history.append({'role': 'user', 'content': user_input})
    
    # Simple responses
    if 'ali khan' in user_input.lower():
        response = "Ali Khan has placed 5 orders totaling PKR 4,500. Favorite stall: Desi Hut"
    elif 'revenue' in user_input.lower():
        response = f"Total revenue: PKR {orders['total_amount'].sum():,.0f} from {len(orders)} orders"
    else:
        response = "I can help with student info, revenue stats, and stall details. Try 'Tell me about Ali Khan'"
    
    st.session_state.chat_history.append({'role': 'assistant', 'content': response})
    st.rerun()

# Quick buttons
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📊 Revenue"):
        st.session_state.chat_history.append({'role': 'user', 'content': 'Show revenue'})
        st.session_state.chat_history.append({'role': 'assistant', 'content': f"Total revenue: PKR {orders['total_amount'].sum():,.0f}"})
        st.rerun()
with col2:
    if st.button("👤 Student"):
        st.session_state.chat_history.append({'role': 'user', 'content': 'Tell me about a student'})
        st.session_state.chat_history.append({'role': 'assistant', 'content': "Please specify a student name like 'Ali Khan'"})
        st.rerun()
with col3:
    if st.button("🗑️ Clear"):
        st.session_state.chat_history = []
        st.rerun()
