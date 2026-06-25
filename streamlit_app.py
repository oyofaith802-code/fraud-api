import streamlit as st
import requests
import numpy as np

API_URL = "https://fraud-api-1d91.onrender.com"

st.title("🚀 Fraud SaaS Dashboard V3")

# =========================
# LOGIN SECTION
# =========================
if "api_key" not in st.session_state:

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
else:

    st.subheader("💰 SaaS Dashboard")

    st.write("API Key:")
    st.code(st.session_state.api_key)

    # =========================
    # INPUTS (ONLY USER FRIENDLY)
    # =========================
    v1 = st.number_input("V1", value=0.0)
    v2 = st.number_input("V2", value=0.0)
    v3 = st.number_input("V3", value=0.0)

    amount = st.number_input("Amount", value=0.01)
    time = st.number_input("Time", value=0.01)

    # =========================
    # BUILD FULL 30 FEATURES
    # =========================
    auto_features = [0.0] * 25  # fills V4–V28

    features = [v1, v2, v3] + auto_features + [time, amount]

    features = np.array([features], dtype=float)

    # =========================
    # PREDICT
    # =========================
    if st.button("Predict Fraud"):

        res = requests.post(
            f"{API_URL}/predict",
            json={"features": features.tolist()},
            headers={"api-key": st.session_state.api_key}
        )

        try:
            st.json(res.json())
        except:
            st.error(res.text)