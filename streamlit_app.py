import streamlit as st
import requests

API_URL = "https://fraud-api-1d91.onrender.com"

st.title("🚀 Fraud SaaS Dashboard V3")

menu = ["Login", "Signup"]
choice = st.sidebar.selectbox("Menu", menu)

# ======================
# SIGNUP
# ======================
if choice == "Signup":
    st.subheader("Create Account")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Signup"):
        res = requests.post(
            f"{API_URL}/signup",
            params={"email": email, "password": password}
        )

        try:
            st.json(res.json())
        except:
            st.error(res.text)

# ======================
# LOGIN
# ======================
if choice == "Login":
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(
            f"{API_URL}/login",
            params={"email": email, "password": password}
        )

        try:
            data = res.json()
        except:
            st.error(res.text)
            st.stop()

        if "api_key" in data:
            st.session_state["api_key"] = data["api_key"]
            st.success("Login successful")
        else:
            st.error(data)

# ======================
# DASHBOARD
# ======================
if "api_key" in st.session_state:

    st.subheader("💰 SaaS Dashboard")

    api_key = st.session_state["api_key"]

    V1 = st.number_input("V1")
    V2 = st.number_input("V2")
    V3 = st.number_input("V3")
    Amount = st.number_input("Amount")
    Time = st.number_input("Time")

    if st.button("Predict Fraud"):
        res = requests.post(
            f"{API_URL}/predict",
            params={
                "V1": V1,
                "V2": V2,
                "V3": V3,
                "Amount": Amount,
                "Time": Time
            },
            headers={"api_key": api_key}
        )

        try:
            st.json(res.json())
        except:
            st.error(res.text)