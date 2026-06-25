import streamlit as st
import requests

API_URL = "https://fraud-api-1d91.onrender.com"

st.title("🚀 Fraud SaaS Dashboard V3")

menu = st.sidebar.selectbox("Menu", ["Login / Signup", "Dashboard"])

# ================= AUTH =================
if menu == "Login / Signup":

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Signup"):

            res = requests.post(
                f"{API_URL}/signup",
                params={"email": email, "password": password}
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
                params={"email": email, "password": password}
            )

            try:
                data = res.json()
                if "api_key" in data:
                    st.session_state.api_key = data["api_key"]
                    st.success("Login successful")
                else:
                    st.error(data)
            except:
                st.error(res.text)

# ================= DASHBOARD =================
if menu == "Dashboard":

    if "api_key" not in st.session_state:
        st.warning("Please login first")
        st.stop()

    st.success("💰 SaaS Dashboard")

    st.write("API KEY:", st.session_state.api_key)

    features = []

    st.subheader("🧪 30 Feature Input")

    for i in range(1, 31):
        features.append(st.number_input(f"V{i}", value=0.0))

    amount = st.number_input("Amount", value=0.0)
    time = st.number_input("Time", value=0.0)

    if st.button("Predict"):

        payload = {
            "features": features + [amount, time]
        }

        res = requests.post(
            f"{API_URL}/predict",
            json=payload,
            headers={"api_key": st.session_state.api_key}
        )

        try:
            st.json(res.json())
        except:
            st.error({
                "error": "Prediction failed",
                "raw": res.text
            })