import streamlit as st
import requests
import numpy as np

API_URL = "https://fraud-api-1d91.onrender.com"

st.set_page_config(page_title="Fraud SaaS V3", layout="centered")

st.title("🚀 Fraud SaaS Dashboard V3")

# =========================
# SESSION
# =========================
if "api_key" not in st.session_state:
    st.session_state.api_key = None


# =========================
# LOGIN / SIGNUP
# =========================
if st.session_state.api_key is None:

    st.subheader("Login / Signup")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            res = requests.post(
                f"{API_URL}/login",
                params={"email": email, "password": password}
            )

            data = res.json()

            if "api_key" in data:
                st.session_state.api_key = data["api_key"]
                st.success("Login successful")
                st.rerun()
            else:
                st.error(data)

    with col2:
        if st.button("Signup"):
            res = requests.post(
                f"{API_URL}/signup",
                params={"email": email, "password": password}
            )

            st.success(res.json())


# =========================
# DASHBOARD
# =========================
else:

    st.subheader("💰 SaaS Dashboard")

    st.code(st.session_state.api_key)

    v1 = st.number_input("V1", value=0.0)
    v2 = st.number_input("V2", value=0.0)
    v3 = st.number_input("V3", value=0.0)

    amount = st.number_input("Amount", value=0.01)
    time = st.number_input("Time", value=0.01)

    v_rest = [0.0] * 25
    features = [v1, v2, v3] + v_rest + [time, amount]

    if st.button("Predict Fraud"):

        res = requests.post(
            f"{API_URL}/predict",
            json={"features": [features]},
            headers={"api-key": st.session_state.api_key}
        )

        st.json(res.json())


if st.button("Logout"):
    st.session_state.api_key = None
    st.rerun()