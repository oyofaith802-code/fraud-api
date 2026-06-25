import streamlit as st
import requests

st.set_page_config(page_title="Fraud API Admin", layout="centered")

st.title("💰 Fraud API SaaS Dashboard")

API_URL = "https://your-render-url.onrender.com/admin/stats"

try:
    data = requests.get(API_URL).json()

    st.metric("Total Users", data["total_users"])
    st.metric("Total Requests", data["total_requests"])
    st.metric("Revenue", f"${data['total_revenue']}")

    st.subheader("System Status")
    st.success("API is running successfully 🚀")

    st.subheader("Monetization Status")
    st.info("Free + Pro system active")

except Exception as e:
    st.error(f"Failed to load data: {e}")