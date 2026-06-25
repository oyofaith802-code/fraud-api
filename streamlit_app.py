import streamlit as st
import requests
import matplotlib.pyplot as plt

API = "https://fraud-api-1d91.onrender.com"

st.set_page_config(layout="wide")

# ---------------- LOGIN ----------------
if "api_key" not in st.session_state:

    st.title("🔐 Fraud SaaS Login")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
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

    with tab2:
        email2 = st.text_input("Signup Email")
        pass2 = st.text_input("Signup Password", type="password")

        if st.button("Create Account"):
            res = requests.post(f"{API}/signup", params={
                "email": email2,
                "password": pass2
            }).json()

            st.success(f"Account created: {res.get('api_key')}")

    st.stop()


# ---------------- DASHBOARD ----------------
data = requests.get(
    f"{API}/user/dashboard",
    params={"api_key": st.session_state.api_key}
).json()

st.title("💰 Fraud Detection SaaS")

col1, col2, col3 = st.columns(3)
col1.metric("Plan", data["plan"])
col2.metric("Used", data["requests_used"])
col3.metric("Remaining", data["remaining"])

# chart
fig, ax = plt.subplots()
ax.bar(["Used", "Remaining"], [data["requests_used"], data["remaining"]])
st.pyplot(fig)

# API KEY
st.subheader("API KEY")
st.code(data["api_key"])

# ---------------- UPGRADE ----------------
st.subheader("🚀 Upgrade")

plan = st.selectbox("Choose plan", ["daily", "monthly"])

if st.button("Pay with Paystack"):
    res = requests.post(f"{API}/pay", params={
        "email": data["email"],
        "plan": plan
    }).json()

    st.write(res)