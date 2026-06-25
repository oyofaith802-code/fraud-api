import streamlit as st
import requests

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Fraud SaaS Dashboard", layout="wide")

st.title("💰 Fraud Detection SaaS Dashboard")

API_URL = "https://fraud-api-1d91.onrender.com/admin/stats"

# -------------------------
# SAFE API CALL
# -------------------------
def fetch_stats():
    try:
        res = requests.get(API_URL, timeout=10)

        if res.status_code != 200:
            return None, f"API Error: {res.status_code}"

        return res.json(), None

    except Exception as e:
        return None, str(e)

# -------------------------
# LOAD DATA
# -------------------------
data, error = fetch_stats()

# -------------------------
# ERROR HANDLING
# -------------------------
if error:
    st.error(f"❌ Failed to load data: {error}")
    st.stop()

# -------------------------
# DASHBOARD UI
# -------------------------
col1, col2, col3 = st.columns(3)

col1.metric("👥 Total Users", data.get("total_users", 0))
col2.metric("📊 Total Requests", data.get("total_requests", 0))
col3.metric("💰 Revenue", f"${data.get('total_revenue', 0)}")

st.divider()

# -------------------------
# STATUS SECTION
# -------------------------
st.subheader("System Status")

st.success("🚀 API is running successfully")

st.info("💡 SaaS Mode: Active (Free + Paid plans supported)")

# -------------------------
# DEBUG SECTION (OPTIONAL)
# -------------------------
with st.expander("🔍 Raw API Response"):
    st.json(data)