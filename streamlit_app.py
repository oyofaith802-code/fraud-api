import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Fraud SaaS Admin", layout="wide")

st.title("💰 Fraud API SaaS Dashboard")

API_URL = "https://fraud-api-1d91.onrender.com/admin/stats"

try:
    data = requests.get(API_URL).json()
except:
    st.error("Failed to load data from API")
    st.stop()

# METRICS
col1, col2, col3 = st.columns(3)

col1.metric("Total Users", data["total_users"])
col2.metric("Total Requests", data["total_requests"])
col3.metric("Revenue (₦/$)", data["total_revenue"])

st.divider()

# -----------------------
# SIMPLE GRAPH (IMPORTANT)
# -----------------------
labels = ["Users", "Requests", "Revenue"]
values = [
    data["total_users"],
    data["total_requests"],
    data["total_revenue"]
]

fig, ax = plt.subplots()
ax.bar(labels, values)
ax.set_title("System Overview")

st.pyplot(fig)

# STATUS
st.success("API Running 🚀")
st.info("Free + Paid SaaS system active")