import streamlit as st
import requests

API = "https://your-api.onrender.com"

st.title("🚀 Fraud SaaS V3 Dashboard")

if "api_key" not in st.session_state:
    st.session_state.api_key = None


# ---------------- LOGIN ----------------
if st.session_state.api_key is None:

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):

            res = requests.post(f"{API}/login", params={
                "email": email,
                "password": password
            })

            try:
                data = res.json()
            except:
                st.error(res.text)
                st.stop()

            if "api_key" in data:
                st.session_state.api_key = data["api_key"]
                st.success("Login successful")
                st.rerun()
            else:
                st.error(data)

    with col2:
        if st.button("Signup"):

            res = requests.post(f"{API}/signup", params={
                "email": email,
                "password": password
            })

            st.write(res.json())

    st.stop()


# ---------------- DASHBOARD ----------------
st.success("Logged in")

api_key = st.session_state.api_key

st.subheader("Test Prediction")

v1 = st.number_input("V1")
v2 = st.number_input("V2")
v3 = st.number_input("V3")
amount = st.number_input("Amount")
time = st.number_input("Time")

if st.button("Predict"):

    res = requests.post(
        f"{API}/predict",
        headers={"api-key": api_key},
        params={
            "V1": v1,
            "V2": v2,
            "V3": v3,
            "Amount": amount,
            "Time": time
        }
    )

    try:
        st.write(res.json())
    except:
        st.error(res.text)


if st.button("Logout"):
    st.session_state.api_key = None
    st.rerun()