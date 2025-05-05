import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os

# Configure page
st.set_page_config(
    page_title="Recommendation Engine Dashboard",
    page_icon="🎯",
    layout="wide"
)

# Constants
API_URL = os.getenv('API_URL', 'http://localhost:8000')
REFRESH_INTERVAL = 60  # seconds

# Helper functions
def get_recommendations(user_id, limit=10):
    """Get recommendations from the API."""
    try:
        response = requests.post(
            f"{API_URL}/recommend",
            json={"user_id": user_id, "limit": limit}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error getting recommendations: {str(e)}")
        return None

def simulate_user_interaction(user_id, item_id):
    """Simulate a user interaction."""
    try:
        # In a real system, this would send an event to Kinesis
        st.success(f"Simulated interaction: User {user_id} interacted with item {item_id}")
    except Exception as e:
        st.error(f"Error simulating interaction: {str(e)}")

# Sidebar
st.sidebar.title("Controls")
user_id = st.sidebar.text_input("User ID", "user_123")
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 10, 300, 60)

# Main content
st.title("🎯 Recommendation Engine Dashboard")

# Metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Active Users", "1,234", "+123")
with col2:
    st.metric("Recommendations Served", "45,678", "+1,234")
with col3:
    st.metric("Average Latency", "150ms", "-10ms")

# Recommendations
st.header("Personalized Recommendations")
recommendations = get_recommendations(user_id)

if recommendations:
    # Create DataFrame for recommendations
    df = pd.DataFrame(recommendations['recommendations'])
    
    # Display recommendations
    for idx, row in df.iterrows():
        with st.expander(f"Item {row['item_id']} (Score: {row['score']:.2f})"):
            st.write(f"Popularity: {row['popularity']['unique_users']} unique users")
            st.write(f"Total Interactions: {row['popularity']['total_interactions']}")
            
            if st.button(f"Simulate Interaction", key=f"btn_{idx}"):
                simulate_user_interaction(user_id, row['item_id'])
    
    # Visualization
    st.subheader("Recommendation Distribution")
    fig = px.bar(
        df,
        x='item_id',
        y='score',
        title='Recommendation Scores'
    )
    st.plotly_chart(fig, use_container_width=True)

# System Metrics
st.header("System Metrics")

# Create sample data for demonstration
metrics_data = pd.DataFrame({
    'timestamp': pd.date_range(start=datetime.now() - timedelta(hours=24), periods=24, freq='H'),
    'latency_ms': [150 + i * 5 for i in range(24)],
    'requests_per_second': [100 + i * 10 for i in range(24)],
    'error_rate': [0.01 + i * 0.001 for i in range(24)]
})

# Latency Chart
st.subheader("Latency Over Time")
fig_latency = px.line(
    metrics_data,
    x='timestamp',
    y='latency_ms',
    title='API Latency (ms)'
)
st.plotly_chart(fig_latency, use_container_width=True)

# Throughput Chart
st.subheader("Request Throughput")
fig_throughput = px.line(
    metrics_data,
    x='timestamp',
    y='requests_per_second',
    title='Requests per Second'
)
st.plotly_chart(fig_throughput, use_container_width=True)

# Error Rate Chart
st.subheader("Error Rate")
fig_errors = px.line(
    metrics_data,
    x='timestamp',
    y='error_rate',
    title='Error Rate (%)'
)
st.plotly_chart(fig_errors, use_container_width=True)

# Auto-refresh
time.sleep(refresh_rate)
st.experimental_rerun() 