import streamlit as st
import requests
import matplotlib.pyplot as plt

API = "https://fraud-api-1d91.onrender.com"

st.set_page_config(page_title="Fraud SaaS", layout="wide")

# ================= SESSION =================
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "email" not in st.session_state:
    st.session_state.email = None

# ================= SAFE REQUEST =================
def safe_post(url, **kwargs):
    try:
        r = requests.post(url, timeout=15, **kwargs)
        return r.status_code, r.json() if "application/json" in r.headers.get("Content-Type","") else None
    except:
        return 500, None

def safe_get(url, **kwargs):
    try:
        r = requests.get(url, timeout=15, **kwargs)
        return r.status_code, r.json() if "application/json" in r.headers.get("Content-Type","") else None
    except:
        return 500, None

# ================= LOGIN / SIGNUP =================
if st.session_state.api_key is None:

    st.title("🚀 Fraud SaaS")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            status, res = safe_post(
                f"{API}/login",
                params={"email": email, "password": password}
            )

            if res and "api_key" in res:
                st.session_state.api_key = res["api_key"]
                st.session_state.email = email
                st.success("Login success")
                st.rerun()
            else:
                st.error("Login failed")

    with tab2:
        email = st.text_input("Email ", key="s1")
        password = st.text_input("Password ", type="password", key="s2")

        if st.button("Signup"):
            status, res = safe_post(
                f"{API}/signup",
                params={"email": email, "password": password}
            )

            st.write(res)

    st.stop()

# ================= DASHBOARD =================
st.title("💰 Fraud Dashboard")

status, data = safe_get(f"{API}/admin/stats")

if not data:
    st.error("Backend error")
    st.stop()

col1, col2, col3 = st.columns(3)

col1.metric("Users", data["total_users"])
col2.metric("Requests", data["total_requests"])
col3.metric("Revenue", data["total_revenue"])

# ================= CHART =================
fig, ax = plt.subplots()
ax.bar(["Revenue", "Requests"], [data["total_revenue"], data["total_requests"]])
st.pyplot(fig)

# ================= API KEY =================
st.subheader("API KEY")
st.code(st.session_state.api_key)

# ================= PREDICT =================
st.subheader("Test Prediction")

v1 = st.number_input("V1")
v2 = st.number_input("V2")
v3 = st.number_input("V3")
amount = st.number_input("Amount")
time = st.number_input("Time")

if st.button("Predict"):

    status, res = safe_post(
        f"{API}/predict",
        headers={"x-api-key": st.session_state.api_key},
        params={
            "V1": v1,
            "V2": v2,
            "V3": v3,
            "Amount": amount,
            "Time": time
        }
    )

    st.write(res)

# ================= PAYSTACK =================
plan = st.selectbox("Plan", ["daily", "monthly"])

if st.button("Upgrade"):

    status, res = safe_post(
        f"{API}/paystack/pay",
        params={
            "email": st.session_state.email,
            "plan": plan
        }
    )

    if res:
        st.write(res)