import streamlit as st
import requests

API = "https://fraud-api-1d91.onrender.com"

st.set_page_config(page_title="Fraud SaaS V3", layout="centered")

st.title("🚀 Fraud SaaS Dashboard V3")

menu = st.sidebar.selectbox("Menu", ["Login", "Signup", "Dashboard"])

# =====================
# SIGNUP
# =====================
if menu == "Signup":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):
        res = requests.post(f"{API}/signup", params={
            "email": email,
            "password": password
        })

        try:
            st.success(res.json())
        except:
            st.error(res.text)


# =====================
# LOGIN
# =====================
if menu == "Login":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(f"{API}/login", params={
            "email": email,
            "password": password
        })

        try:
            data = res.json()

            if "api_key" in data:
                st.session_state["api_key"] = data["api_key"]
                st.success("Login successful")
            else:
                st.error(data)

        except:
            st.error(res.text)


# =====================
# DASHBOARD
# =====================
if menu == "Dashboard":

    if "api_key" not in st.session_state:
        st.warning("Login first")
        st.stop()

    st.success("💰 SaaS Dashboard")

    api_key = st.session_state["api_key"]

    st.write("API KEY:", api_key)

    st.subheader("🧪 Test Prediction (30 Features)")

    features = []

    for i in range(30):
        features.append(st.number_input(f"V{i+1}", value=0.0))

    amount = st.number_input("Amount", 0.0)
    time = st.number_input("Time", 0.0)

    features[28] = amount
    features[29] = time

    if st.button("Predict Fraud"):

        res = requests.post(
            f"{API}/predict",
            json={"features": features},
            headers={"api_key": api_key}
        )

        try:
            st.json(res.json())
        except:
            st.error(res.text)