import streamlit as st
import requests
import numpy as np

API_URL = "https://fraud-api-1d91.onrender.com"

st.set_page_config(page_title="Fraud SaaS V3", layout="centered")

st.title("🚀 Fraud SaaS Dashboard V3")

# =========================
# SESSION STATE
# =========================
if "api_key" not in st.session_state:
    st.session_state.api_key = None


# =========================
# LOGIN / SIGNUP PAGE
# =========================
if st.session_state.api_key is None:

    st.subheader("Login / Signup")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    # =========================
    # LOGIN
    # =========================
    with col1:
        if st.button("Login"):

            try:
                res = requests.post(
                    f"{API_URL}/login",
                    params={
                        "email": email,
                        "password": password
                    }
                )

                data = res.json()

                if "api_key" in data:
                    st.session_state.api_key = data["api_key"]
                    st.success("Login successful 🚀")
                    st.rerun()
                else:
                    st.error(data)

            except Exception as e:
                st.error(str(e))


    # =========================
    # SIGNUP
    # =========================
    with col2:
        if st.button("Signup"):

            try:
                res = requests.post(
                    f"{API_URL}/signup",
                    params={
                        "email": email,
                        "password": password
                    }
                )

                st.success(res.json())

            except Exception as e:
                st.error(str(e))


# =========================
# DASHBOARD
# =========================
else:

    st.subheader("💰 SaaS Fraud Dashboard")

    st.write("Your API Key:")
    st.code(st.session_state.api_key)

    # =========================
    # INPUTS (USER FRIENDLY)
    # =========================
    v1 = st.number_input("V1", value=0.0)
    v2 = st.number_input("V2", value=0.0)
    v3 = st.number_input("V3", value=0.0)

    amount = st.number_input("Amount", value=0.01)
    time = st.number_input("Time", value=0.01)

    # =========================
    # BUILD FULL 30 FEATURES
    # =========================
    v_rest = [0.0] * 25  # V4–V28

    features = [v1, v2, v3] + v_rest + [time, amount]

    features = np.array([features], dtype=float)

    # =========================
    # PREDICT
    # =========================
    if st.button("Predict Fraud"):

        try:
            res = requests.post(
                f"{API_URL}/predict",
                json={
                    "features": features.tolist()
                },
                headers={
                    "api-key": st.session_state.api_key
                }
            )

            data = res.json()
            st.json(data)

        except Exception as e:
            st.error(str(e))


# =========================
# LOGOUT
# =========================
if st.session_state.api_key:
    if st.button("Logout"):
        st.session_state.api_key = None
        st.rerun()