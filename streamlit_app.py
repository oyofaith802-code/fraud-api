import streamlit as st
import requests

API_URL = "https://fraud-api-1d91.onrender.com"

st.set_page_config(page_title="Fraud SaaS V3", layout="centered")

st.title("🚀 Fraud SaaS Dashboard V3")

if "api_key" not in st.session_state:
    st.session_state.api_key = None

menu = st.sidebar.selectbox("Menu", ["Login", "Signup", "Dashboard"])


# =========================
# SIGNUP
# =========================
if menu == "Signup":
    st.subheader("Create Account")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Signup"):
        res = requests.post(
            f"{API_URL}/signup",
            params={"email": email, "password": password}
        )

        try:
            data = res.json()
        except:
            st.error(res.text)
            st.stop()

        st.json(data)


# =========================
# LOGIN
# =========================
if menu == "Login":
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(
            f"{API_URL}/login",
            params={"email": email, "password": password}
        )

        data = res.json()

        if "api_key" in data:
            st.session_state.api_key = data["api_key"]
            st.success("Login successful")
        else:
            st.error(data)


# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":

    if not st.session_state.api_key:
        st.warning("Login first")
        st.stop()

    st.subheader("💰 SaaS Dashboard")

    v1 = st.number_input("V1", value=0.0)
    v2 = st.number_input("V2", value=0.0)
    v3 = st.number_input("V3", value=0.0)
    amount = st.number_input("Amount", value=0.01)
    time = st.number_input("Time", value=0.01)

    if st.button("Predict"):
        res = requests.post(
            f"{API_URL}/predict",
            params={
                "V1": v1,
                "V2": v2,
                "V3": v3,
                "Amount": amount,
                "Time": time
            },
            headers={
                "api-key": st.session_state.api_key
            }
        )

        try:
            st.json(res.json())
        except:
            st.error(res.text)