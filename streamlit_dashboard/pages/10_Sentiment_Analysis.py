"""
Sentiment Analysis on Ratings and Comments
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

st.set_page_config(page_title="Sentiment Analysis", page_icon="💭", layout="wide")

st.title("💭 Sentiment Analysis & Customer Feedback")

# Load data
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'campuseats.db')

@st.cache_data(ttl=3600)
def load_data():
    conn = sqlite3.connect(db_path)
    ratings = pd.read_sql_query('SELECT * FROM ratings', conn)
    orders = pd.read_sql_query('SELECT * FROM orders', conn)
    stalls = pd.read_sql_query('SELECT * FROM stalls', conn)
    conn.close()
    return ratings, orders, stalls

ratings, orders, stalls = load_data()

# Simple sentiment function
def get_sentiment(text):
    if pd.isna(text) or text == '':
        return 'Neutral'
    
    positive_words = ['good', 'great', 'amazing', 'excellent', 'love', 'best', 'awesome', 'delicious', 'tasty', 'fast']
    negative_words = ['bad', 'poor', 'slow', 'cold', 'rude', 'expensive', 'terrible', 'worst', 'awful']
    
    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        return 'Positive 😊'
    elif neg_count > pos_count:
        return 'Negative 😞'
    else:
        return 'Neutral 😐'

# Apply sentiment
if len(ratings) > 0 and 'comment' in ratings.columns:
    ratings['sentiment'] = ratings['comment'].apply(get_sentiment)

# Tabs
tab1, tab2, tab3 = st.tabs(["😊 Sentiment Overview", "⭐ Rating Analysis", "💬 Comments"])

# ===== TAB 1: SENTIMENT OVERVIEW =====
with tab1:
    st.subheader("Customer Sentiment Overview")
    
    if len(ratings) > 0 and 'sentiment' in ratings.columns:
        sentiment_counts = ratings['sentiment'].value_counts()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            pos_count = sentiment_counts.get('Positive 😊', 0)
            st.metric("😊 Positive", pos_count, f"{(pos_count/len(ratings)*100):.1f}%")
        
        with col2:
            neg_count = sentiment_counts.get('Negative 😞', 0)
            st.metric("😞 Negative", neg_count, f"{(neg_count/len(ratings)*100):.1f}%")
        
        with col3:
            neu_count = sentiment_counts.get('Neutral 😐', 0)
            st.metric("😐 Neutral", neu_count, f"{(neu_count/len(ratings)*100):.1f}%")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(values=sentiment_counts.values, names=sentiment_counts.index,
                        title='Sentiment Distribution',
                        color_discrete_sequence=['#4ECDC4', '#FF6B6B', '#95A5A6'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'rating' in ratings.columns:
                sentiment_by_rating = ratings.groupby('rating')['sentiment'].value_counts().unstack().fillna(0)
                fig = px.bar(sentiment_by_rating, title='Sentiment by Rating',
                            labels={'value': 'Count', 'rating': 'Rating'},
                            barmode='stack')
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No ratings with comments available for sentiment analysis")

# ===== TAB 2: RATING ANALYSIS =====
with tab2:
    st.subheader("Rating Analysis")
    
    if len(ratings) > 0:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_rating = ratings['rating'].mean()
            st.metric("Average Rating", f"{avg_rating:.2f}⭐", "out of 5.0")
        
        with col2:
            five_star = len(ratings[ratings['rating'] == 5])
            st.metric("5-Star Ratings", five_star, f"{(five_star/len(ratings)*100):.1f}%")
        
        with col3:
            one_star = len(ratings[ratings['rating'] == 1])
            st.metric("1-Star Ratings", one_star, f"{(one_star/len(ratings)*100):.1f}%")
        
        # Rating distribution
        rating_dist = ratings['rating'].value_counts().sort_index()
        
        fig = px.bar(x=rating_dist.index, y=rating_dist.values,
                    title='Rating Distribution',
                    labels={'x': 'Rating', 'y': 'Number of Reviews'},
                    color=rating_dist.index,
                    color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
        
        # Stall ratings - using px.bar instead of barh
        stall_ratings = ratings.groupby('stall_id')['rating'].mean().reset_index()
        stall_ratings = stall_ratings.sort_values('rating', ascending=False).head(10)
        
        # Map stall names
        stall_name_map = dict(zip(stalls['stall_id'], stalls['stall_name']))
        stall_ratings['stall_name'] = stall_ratings['stall_id'].map(stall_name_map)
        
        # Use bar chart (horizontal via orientation='h')
        fig = px.bar(stall_ratings, x='rating', y='stall_name',
                     title='Top 10 Highest Rated Stalls',
                     color='rating',
                     orientation='h',
                     color_continuous_scale='Greens')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No ratings available")

# ===== TAB 3: COMMENTS =====
with tab3:
    st.subheader("Customer Comments")
    
    if len(ratings) > 0 and 'comment' in ratings.columns:
        comments_df = ratings[ratings['comment'].notna()].copy()
        comments_df['sentiment'] = comments_df['comment'].apply(get_sentiment)
        
        sentiment_filter = st.selectbox(
            "Filter by Sentiment",
            ['All', 'Positive 😊', 'Negative 😞', 'Neutral 😐']
        )
        
        if sentiment_filter != 'All':
            filtered = comments_df[comments_df['sentiment'] == sentiment_filter]
        else:
            filtered = comments_df
        
        st.write(f"**Showing {len(filtered)} comments**")
        
        for idx, row in filtered.head(20).iterrows():
            emoji = "😊" if row['sentiment'] == 'Positive 😊' else "😞" if row['sentiment'] == 'Negative 😞' else "😐"
            st.write(f"{emoji} **Rating:** {row['rating']}⭐")
            st.write(f"**Comment:** \"{row['comment']}\"")
            st.markdown("---")
    else:
        st.info("No comments available")
