import streamlit as st
import requests

API_URL = "https://fraud-api-1d91.onrender.com"

st.set_page_config(page_title="Fraud SaaS V3", layout="centered")

st.title("🚀 Fraud SaaS Dashboard V3")

# =========================
# SESSION STATE
# =========================
if "api_key" not in st.session_state:
    st.session_state.api_key = None


# =========================
# AUTH SECTION
# =========================
menu = st.sidebar.selectbox("Menu", ["Login", "Signup", "Dashboard"])


# =========================
# SIGNUP
# =========================
if menu == "Signup":
    st.subheader("Create Account")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Signup"):
        try:
            res = requests.post(
                f"{API_URL}/signup",
                params={"email": email, "password": password}
            )

            data = res.json()

            if "api_key" in data:
                st.success("Account created!")
                st.write("Your API Key:")
                st.code(data["api_key"])

            else:
                st.error(data)

        except Exception as e:
            st.error(str(e))


# =========================
# LOGIN
# =========================
if menu == "Login":
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            res = requests.post(
                f"{API_URL}/login",
                params={"email": email, "password": password}
            )

            data = res.json()

            if "api_key" in data:
                st.session_state.api_key = data["api_key"]
                st.success("Login successful!")

            else:
                st.error(data)

        except Exception as e:
            st.error(str(e))


# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":

    if not st.session_state.api_key:
        st.warning("Please login first")
        st.stop()

    st.subheader("💰 SaaS Dashboard")

    # Inputs
    v1 = st.number_input("V1", value=0.0)
    v2 = st.number_input("V2", value=0.0)
    v3 = st.number_input("V3", value=0.0)
    amount = st.number_input("Amount", value=0.01)
    time = st.number_input("Time", value=0.01)

    if st.button("Predict Fraud"):

        try:
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
                    "api_key": st.session_state.api_key
                }
            )

            # SAFE PARSING (fix your JSON crash)
            try:
                data = res.json()
            except:
                st.error("Server returned invalid JSON")
                st.text(res.text)
                st.stop()

            st.json(data)

        except Exception as e:
            st.error(str(e))