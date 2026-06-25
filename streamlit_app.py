import streamlit as st
import requests

# -------------------------
# CONFIG
# -------------------------
API_URL = "https://fraud-api-1d91.onrender.com/admin/stats"

# -------------------------
# ADMIN LOGIN
# -------------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

st.title("💰 Fraud API Admin Dashboard")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def login():
    st.subheader("Admin Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")


# -------------------------
# DASHBOARD
# -------------------------
def dashboard():

    st.sidebar.success("Logged in as Admin")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.subheader("📊 System Overview")

    try:
        data = requests.get(API_URL).json()

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Users", data["total_users"])
        col2.metric("Total Requests", data["total_requests"])
        col3.metric("Revenue ($)", data["total_revenue"])

        st.divider()

        st.subheader("📈 Live Stats")

        st.line_chart({
            "Users": [data["total_users"]],
            "Requests": [data["total_requests"]],
            "Revenue": [data["total_revenue"]]
        })

        st.success("System Running Smoothly 🚀")

    except Exception as e:
        st.error(f"Error fetching data: {e}")


# -------------------------
# APP FLOW
# -------------------------
if not st.session_state.logged_in:
    login()
else:
    dashboard()