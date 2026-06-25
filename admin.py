import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Fraud SaaS Dashboard", layout="wide")

st.title("💰 Fraud Detection SaaS Dashboard")

API_URL = "https://fraud-api-1d91.onrender.com/admin/stats"

try:
    data = requests.get(API_URL).json()
except:
    st.error("API not reachable")
    st.stop()

# METRICS
col1, col2 = st.columns(2)

col1.metric("Total Users", data["total_users"])
col2.metric("Total Requests", data["total_requests"])

# CHART
st.subheader("Usage Analytics")

fig, ax = plt.subplots()
ax.bar(["Users", "Requests"], [data["total_users"], data["total_requests"]])
st.pyplot(fig)

st.success("System running 🚀")