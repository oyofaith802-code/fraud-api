import streamlit as st
import requests
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
API = "https://fraud-api-1d91.onrender.com"

st.set_page_config(page_title="Fraud SaaS Dashboard", layout="wide")


# =========================================================
# SESSION STATE
# =========================================================
if "api_key" not in st.session_state:
    st.session_state.api_key = None


# =========================================================
# SIGNUP PAGE
# =========================================================
if st.session_state.api_key is None:

    st.title("🚀 Fraud API SaaS")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    # ---------------- LOGIN ----------------
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            res = requests.post(f"{API}/login", params={
                "email": email,
                "password": password
            }).json()

            if "api_key" in res:
                st.session_state.api_key = res["api_key"]
                st.success("Login successful")
                st.rerun()
            else:
                st.error(res)

    # ---------------- SIGNUP ----------------
    with tab2:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Create Account"):
            res = requests.post(f"{API}/signup", params={
                "email": email,
                "password": password
            }).json()

            st.success(res)


        code = st.text_input("Verification Code")

        if st.button("Verify Email"):
            res = requests.post(f"{API}/verify", params={
                "email": email,
                "code": code
            }).json()

            st.write(res)


    st.stop()


# =========================================================
# DASHBOARD DATA
# =========================================================
st.title("💰 SaaS Fraud Detection Dashboard")

data = requests.get(
    f"{API}/admin/stats"
).json()


# =========================================================
# METRICS
# =========================================================
col1, col2, col3 = st.columns(3)

col1.metric("Total Users", data["total_users"])
col2.metric("Total Requests", data["total_requests"])
col3.metric("Revenue", f"${data['total_revenue']}")


# =========================================================
# REVENUE CHART
# =========================================================
st.subheader("📊 Revenue Overview")

fig, ax = plt.subplots()

ax.bar(
    ["Revenue", "Requests"],
    [data["total_revenue"], data["total_requests"]]
)

st.pyplot(fig)


# =========================================================
# API KEY + USAGE SECTION
# =========================================================
st.subheader("🔑 API Usage")

api_key = st.session_state.api_key

st.code(api_key)


# =========================================================
# TEST PREDICTION PANEL
# =========================================================
st.subheader("🧪 Test Prediction")

col1, col2 = st.columns(2)

with col1:
    v1 = st.number_input("V1")
    v2 = st.number_input("V2")
    v3 = st.number_input("V3")

with col2:
    amount = st.number_input("Amount")
    time = st.number_input("Time")

if st.button("Run Prediction"):
    res = requests.post(
        f"{API}/predict",
        headers={"api-key": api_key},
        params={
            "V1": v1,
            "V2": v2,
            "V3": v3,
            "Amount": amount,
            "Time": time
        }
    ).json()

    st.write(res)


# =========================================================
# UPGRADE (PAYSTACK)
# =========================================================
st.subheader("🚀 Upgrade Plan")

plan = st.selectbox("Choose Plan", ["daily", "monthly"])

if st.button("Upgrade with Paystack"):
    res = requests.post(f"{API}/paystack/pay", params={
        "email": "user@example.com",
        "plan": plan
    }).json()

    st.write("Paystack Link:")
    st.write(res["data"]["authorization_url"])


# =========================================================
# LOGOUT
# =========================================================
if st.button("Logout"):
    st.session_state.api_key = None
    st.rerun()