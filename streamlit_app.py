import streamlit as st
import requests

API_URL = "https://fraud-api-1d91.onrender.com"

st.set_page_config(page_title="Fraud SaaS V3", layout="centered")
st.title("🚀 Fraud SaaS Dashboard V3")

if "api_key" not in st.session_state:
    st.session_state.api_key = None

menu = st.sidebar.selectbox("Menu", ["Login / Signup", "Dashboard"])

if menu == "Login / Signup":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Signup"):
            res = requests.post(
                f"{API_URL}/signup",
                params={"email": email, "password": password},
                timeout=20
            )
            try:
                data = res.json()
                if "api_key" in data:
                    st.session_state.api_key = data["api_key"]
                    st.success("Account created")
                else:
                    st.error(data)
            except:
                st.error(res.text)

    with col2:
        if st.button("Login"):
            res = requests.post(
                f"{API_URL}/login",
                params={"email": email, "password": password},
                timeout=20
            )
            try:
                data = res.json()
                if "api_key" in data:
                    st.session_state.api_key = data["api_key"]
                    st.success("Login successful")
                    st.rerun()
                else:
                    st.error(data)
            except:
                st.error(res.text)

if menu == "Dashboard":
    if not st.session_state.api_key:
        st.warning("Please login first")
        st.stop()

    st.write("API KEY:", st.session_state.api_key)

    features = [st.number_input(f"V{i}", value=0.0) for i in range(1, 29)]
    time = st.number_input("Time", value=0.0)
    amount = st.number_input("Amount", value=0.0)

    if st.button("Predict Fraud"):
        payload = {"features": features + [time, amount]}
        res = requests.post(
            f"{API_URL}/predict",
            json=payload,
            headers={"api_key": st.session_state.api_key},
            timeout=20
        )
        try:
            st.json(res.json())
        except:
            st.error(res.text)