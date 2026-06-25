import streamlit as st
import requests
import numpy as np
import matplotlib.pyplot as plt

API_URL = "https://fraud-api-1d91.onrender.com"

st.set_page_config(page_title="Fraud SaaS V6", layout="wide")

st.title("🚀 Fraud SaaS Dashboard V6")

# ======================
# SESSION
# ======================
if "api_key" not in st.session_state:
    st.session_state.api_key = None


# ======================
# LOGIN / SIGNUP
# ======================
menu = st.sidebar.selectbox("Menu", ["Login / Signup", "Dashboard"])

if menu == "Login / Signup":

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            res = requests.post(f"{API_URL}/login", params={
                "email": email,
                "password": password
            })

            try:
                data = res.json()
                if "api_key" in data:
                    st.session_state.api_key = data["api_key"]
                    st.success("Login successful")
                else:
                    st.error(data)
            except:
                st.error("Server error")

    with col2:
        if st.button("Signup"):
            res = requests.post(f"{API_URL}/signup", params={
                "email": email,
                "password": password
            })

            try:
                st.success(res.json())
            except:
                st.error("Signup failed")


# ======================
# DASHBOARD
# ======================
if menu == "Dashboard":

    if not st.session_state.api_key:
        st.warning("Please login first")
        st.stop()

    st.success(f"API KEY: {st.session_state.api_key}")

    st.subheader("🧪 Prediction (30 Features)")

    features = []
    cols = st.columns(5)

    for i in range(30):
        with cols[i % 5]:
            features.append(st.number_input(f"V{i+1}", value=0.0))

    if st.button("Predict Fraud"):

        payload = {"features": features}

        res = requests.post(
            f"{API_URL}/predict",
            json=payload,
            headers={"X-API-Key": st.session_state.api_key}
        )

        try:
            data = res.json()
            st.json(data)

            if "fraud_score" in data:

                st.subheader("📊 Result Explanation")

                score = data["fraud_score"]

                if score > 0.7:
                    st.error("🚨 HIGH FRAUD RISK")
                    explanation = "Model detected strong anomaly patterns."
                elif score > 0.3:
                    st.warning("⚠️ MEDIUM RISK")
                    explanation = "Some unusual behavior detected."
                else:
                    st.success("✅ LOW RISK")
                    explanation = "Transaction looks normal."

                st.write(explanation)

        except:
            st.error("Invalid JSON response")


    # ======================
    # ANALYTICS
    # ======================
    st.subheader("📊 Analytics")

    stats = requests.get(
        f"{API_URL}/stats",
        params={"api_key": st.session_state.api_key}
    ).json()

    st.write(stats)

    fraud = stats.get("fraud_cases", 0)
    normal = stats.get("normal_cases", 0)

    fig, ax = plt.subplots()

    if fraud == 0 and normal == 0:
        ax.text(0.5, 0.5, "No data yet", ha="center")
    else:
        ax.pie(
            [fraud, normal],
            labels=["Fraud", "Normal"],
            autopct="%1.1f%%"
        )

    st.pyplot(fig)