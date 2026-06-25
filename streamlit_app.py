import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

API_URL = "https://fraud-api-1d91.onrender.com"

st.set_page_config(page_title="Fraud SaaS V5", layout="wide")

st.title("🚀 Fraud SaaS Dashboard V5")

if "api_key" not in st.session_state:
    st.session_state.api_key = None

menu = st.sidebar.radio("Menu", ["Login / Signup", "Dashboard"])

# ======================
# LOGIN / SIGNUP
# ======================
if menu == "Login / Signup":

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Signup"):
            r = requests.post(f"{API_URL}/signup", params={"email": email, "password": password})
            data = r.json()

            if "api_key" in data:
                st.session_state.api_key = data["api_key"]
                st.success("Signup success")
            else:
                st.error(data)

    with col2:
        if st.button("Login"):
            r = requests.post(f"{API_URL}/login", params={"email": email, "password": password})
            data = r.json()

            if "api_key" in data:
                st.session_state.api_key = data["api_key"]
                st.success("Login success")
            else:
                st.error(data)

# ======================
# DASHBOARD
# ======================
if menu == "Dashboard":

    if not st.session_state.api_key:
        st.warning("Login first")
        st.stop()

    api_key = st.session_state.api_key

    st.success(f"API KEY: {api_key}")

    # ======================
    # STATS
    # ======================
    st.subheader("📊 Usage Analytics")

    stats = requests.get(f"{API_URL}/stats", params={"api_key": api_key}).json()

    col1, col2, col3 = st.columns(3)
    col1.metric("Requests", stats["total_requests"])
    col2.metric("Fraud Cases", stats["fraud_cases"])
    col3.metric("Normal Cases", stats["normal_cases"])

    # ======================
    total = fraud + normal

if total > 0:

    fig, ax = plt.subplots()

    ax.pie(
        [fraud, normal],
        labels=["Fraud", "Normal"],
        autopct="%1.1f%%"
    )

    st.pyplot(fig)

else:
    st.warning("No predictions yet. Run a prediction first.")

    # ======================
    # PREDICTION INPUT
    # ======================
    st.subheader("🧪 Predict Fraud (30 Features)")

    features = []

    for i in range(30):
        features.append(st.number_input(f"V{i+1}", value=0.0))

    amount = st.number_input("Amount", value=0.0)
    time = st.number_input("Time", value=0.0)

    features[-2] = amount
    features[-1] = time

    if st.button("Predict"):

        r = requests.post(
            f"{API_URL}/predict",
            json={"features": features},
            headers={"X-API-Key": api_key}
        )

        data = r.json()
        st.json(data)

        if "fraud_score" in data:

            score = data["fraud_score"]

            # BAR GRAPH
            fig, ax = plt.subplots()
            ax.bar(["Risk"], [score], color="red" if score > 0.5 else "green")
            ax.set_ylim(0, 1)
            st.pyplot(fig)

            # EXPLANATION
            st.subheader("🧠 AI Explanation")

            if score > 0.7:
                st.error("High fraud risk")
            elif score > 0.4:
                st.warning("Medium risk")
            else:
                st.success("Low risk")