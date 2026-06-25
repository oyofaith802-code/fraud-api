import streamlit as st
import requests
import matplotlib.pyplot as plt

API = "https://your-render-url.onrender.com"

st.set_page_config(layout="wide")

# LOGIN
if "api_key" not in st.session_state:

    st.title("🔐 Fraud SaaS Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(f"{API}/login", params={
            "email": email,
            "password": password
        }).json()

        if "api_key" in res:
            st.session_state.api_key = res["api_key"]
            st.rerun()
        else:
            st.error("Login failed")

    st.stop()


# DASHBOARD
data = requests.get(
    f"{API}/user/dashboard",
    params={"api_key": st.session_state.api_key}
).json()

st.title("💰 Fraud Detection SaaS Dashboard")

col1, col2, col3 = st.columns(3)
col1.metric("Plan", data["plan"])
col2.metric("Used", data["requests_used"])
col3.metric("Remaining", data["remaining"])

# CHART
fig, ax = plt.subplots()
ax.bar(["Used", "Remaining"], [data["requests_used"], data["remaining"]])
st.pyplot(fig)

# API KEY
st.subheader("🔑 API KEY")
st.code(data["api_key"])

# UPGRADE
if st.button("🚀 Upgrade to PRO"):
    res = requests.post(f"{API}/upgrade", params={
        "email": data["email"],
        "plan": "pro"
    }).json()

    st.write(res)