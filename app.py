import streamlit as st
import requests

API_URL = "https://fraud-api-1d91.onrender.com"

st.title("🚀 Fraud SaaS Dashboard V3")

# =========================
# SESSION STATE
# =========================
if "api_key" not in st.session_state:
    st.session_state.api_key = None

menu = st.sidebar.selectbox("Menu", ["Login", "Signup", "Dashboard"])

# =========================
# SIGNUP
# =========================
if menu == "Signup":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):
        res = requests.post(
            f"{API_URL}/signup",
            params={"email": email, "password": password}
        )

        try:
            data = res.json()
        except:
            st.error("Server error")
            st.stop()

        if "api_key" in data:
            st.success("Account created!")
            st.write("API KEY:", data["api_key"])
        else:
            st.error(data)

# =========================
# LOGIN
# =========================
elif menu == "Login":
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
            st.error("Server error")
            st.stop()

        if "api_key" in data:
            st.session_state.api_key = data["api_key"]
            st.success("Login successful")
            st.rerun()
        else:
            st.error(data)

# =========================
# DASHBOARD
# =========================
elif menu == "Dashboard":

    if not st.session_state.api_key:
        st.warning("Please login first")
        st.stop()

    st.write("💰 SaaS Dashboard")
    st.write("API KEY:", st.session_state.api_key)

    # 30 FEATURES
    features = []
    for i in range(1, 31):
        features.append(st.number_input(f"V{i}", value=0.0))

    amount = st.number_input("Amount", value=0.0)
    time = st.number_input("Time", value=0.0)

    if st.button("Predict Fraud"):
        payload = {
            "features": features
        }

        headers = {
            "api_key": st.session_state.api_key
        }

        res = requests.post(
            f"{API_URL}/predict",
            json=payload,
            headers=headers
        )

        try:
            data = res.json()
        except:
            st.error("Invalid JSON from server")
            st.write(res.text)
            st.stop()

        st.json(data)