"""
Advanced AI Chatbot with NLP capabilities
"""

import streamlit as st
import pandas as pd
import sqlite3
import re
import os
from datetime import datetime

st.set_page_config(page_title="Advanced Chatbot", page_icon="🤖", layout="wide")

st.title("🤖 Advanced AI Chatbot with NLP")

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

# ========== CHATBOT CLASS ==========

class CampusEatsNLP:
    def __init__(self, orders, students, stalls, universities, ratings, categories, order_items):
        self.orders = orders
        self.students = students
        self.stalls = stalls
        self.universities = universities
        self.ratings = ratings
        self.categories = categories
        self.order_items = order_items
    
    def get_student_info(self, name):
        """Get student information"""
        student = self.students[self.students['student_name'].str.lower() == name.lower()]
        if len(student) == 0:
            return None
        student = student.iloc[0]
        student_orders = self.orders[self.orders['student_id'] == student['student_id']]
        
        total_orders = len(student_orders)
        total_spent = student['total_spending']
        avg_order = student_orders['total_amount'].mean() if total_orders > 0 else 0
        uni_name = self.universities[self.universities['university_id'] == student['university_id']]['university_name'].values[0]
        
        return f"""
👤 **{student['student_name']}**
- Total Orders: {total_orders}
- Total Spent: PKR {total_spent:,.0f}
- Avg Order: PKR {avg_order:,.0f}
- University: {uni_name}
        """
    
    def get_stall_info(self, name):
        """Get stall information"""
        stall = self.stalls[self.stalls['stall_name'].str.lower() == name.lower()]
        if len(stall) == 0:
            return None
        stall = stall.iloc[0]
        stall_orders = self.orders[self.orders['stall_id'] == stall['stall_id']]
        stall_ratings = self.ratings[self.ratings['stall_id'] == stall['stall_id']]
        
        avg_rating = stall_ratings['rating'].mean() if len(stall_ratings) > 0 else 0
        total_orders = len(stall_orders)
        total_revenue = stall_orders['total_amount'].sum()
        category_name = self.categories[self.categories['category_id'] == stall['category_id']]['category_name'].values[0]
        
        return f"""
🏪 **{stall['stall_name']}**
- Category: {category_name}
- Total Orders: {total_orders}
- Total Revenue: PKR {total_revenue:,.0f}
- Average Rating: {avg_rating:.1f}⭐ ({len(stall_ratings)} reviews)
        """
    
    def get_stats(self):
        """Get system statistics"""
        total_revenue = self.orders['total_amount'].sum()
        total_orders = len(self.orders)
        total_students = len(self.students)
        total_stalls = len(self.stalls)
        avg_order = self.orders['total_amount'].mean()
        
        return f"""
📊 **System Statistics**
- Total Revenue: PKR {total_revenue:,.0f}
- Total Orders: {total_orders}
- Total Students: {total_students}
- Total Stalls: {total_stalls}
- Average Order Value: PKR {avg_order:,.0f}
        """
    
    def get_top_items(self):
        """Get top selling items"""
        top = self.order_items.groupby('item_name')['quantity'].sum().nlargest(5)
        result = "🍕 **Top 5 Items:**\n"
        for i, (item, qty) in enumerate(top.items(), 1):
            result += f"{i}. {item} ({int(qty)} sold)\n"
        return result
    
    def process_query(self, query):
        """Process natural language query"""
        query_lower = query.lower()
        
        # Check for student query
        for student in self.students['student_name'].values:
            if student.lower() in query_lower:
                info = self.get_student_info(student)
                if info:
                    return info
        
        # Check for stall query
        for stall in self.stalls['stall_name'].values:
            if stall.lower() in query_lower:
                info = self.get_stall_info(stall)
                if info:
                    return info
        
        # Check for statistics
        if any(word in query_lower for word in ['revenue', 'stats', 'statistics', 'total']):
            return self.get_stats()
        
        # Check for top items
        if any(word in query_lower for word in ['top', 'popular', 'best', 'items']):
            return self.get_top_items()
        
        return self.get_help()
    
    def get_help(self):
        return """
🤖 **I can help you with:**

**Student Info:** "Tell me about Ali Khan"
**Stall Info:** "Show Desi Hut details"  
**Statistics:** "Show me revenue stats"
**Top Items:** "What are the top items?"

Try asking something!
        """

# Initialize chatbot
chatbot = CampusEatsNLP(orders, students, stalls, universities, ratings, categories, order_items)

# Sidebar
st.sidebar.write("### 📊 Quick Stats")
st.sidebar.metric("Total Orders", len(orders))
st.sidebar.metric("Total Revenue", f"PKR {orders['total_amount'].sum():,.0f}")
st.sidebar.metric("Avg Order", f"PKR {orders['total_amount'].mean():,.0f}")

# Chat interface
st.write("### 💬 Chat with AI")

if 'nlp_chat' not in st.session_state:
    st.session_state.nlp_chat = []

# Display chat
for msg in st.session_state.nlp_chat:
    if msg['role'] == 'user':
        st.write(f"👤 **You**: {msg['text']}")
    else:
        st.write(f"🤖 **AI**: {msg['text']}")
    st.divider()

# Input
user_query = st.text_input("Ask something...", placeholder="e.g., Tell me about Ali Khan")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("👤 Student"):
        st.session_state.nlp_chat.append({'role': 'user', 'text': 'Tell me about a student'})
        st.session_state.nlp_chat.append({'role': 'assistant', 'text': "Which student? Try 'Ali Khan'"})
        st.rerun()

with col2:
    if st.button("🏪 Stall"):
        st.session_state.nlp_chat.append({'role': 'user', 'text': 'Show me a stall'})
        st.session_state.nlp_chat.append({'role': 'assistant', 'text': "Which stall? Try 'Desi Hut'"})
        st.rerun()

with col3:
    if st.button("📊 Stats"):
        response = chatbot.get_stats()
        st.session_state.nlp_chat.append({'role': 'user', 'text': 'Show me statistics'})
        st.session_state.nlp_chat.append({'role': 'assistant', 'text': response})
        st.rerun()

with col4:
    if st.button("🗑️ Clear"):
        st.session_state.nlp_chat = []
        st.rerun()

if user_query:
    st.session_state.nlp_chat.append({'role': 'user', 'text': user_query})
    response = chatbot.process_query(user_query)
    st.session_state.nlp_chat.append({'role': 'assistant', 'text': response})
    st.rerun()
