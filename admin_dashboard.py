import streamlit as st
import requests

st.title("💰 Fraud API SaaS Dashboard")

API_URL = "https://your-render-url.onrender.com/admin/stats"

data = requests.get(API_URL).json()

st.metric("Total Users", data["total_users"])
st.metric("Total Requests", data["total_requests"])
st.metric("Revenue", f"${data['total_revenue']}")

st.subheader("System Status")
st.success("API is running successfully 🚀")

st.subheader("Monetization Status")
st.info("Free + Pro system active")