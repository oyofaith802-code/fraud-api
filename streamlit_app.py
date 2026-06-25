import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Fraud Detection System", layout="wide")

API_URL = "https://fraud-api-1d91.onrender.com/predict"
API_KEY = "my_secret_12345"

st.title("💳 Bank-Grade Fraud Detection Dashboard")

st.markdown("Enter transaction details below to analyze fraud risk.")

# INPUT FORM
with st.form("fraud_form"):
    cols = st.columns(4)

    inputs = {}

    feature_names = [
        "V1","V2","V3","V4","V5","V6","V7","V8",
        "V9","V10","V11","V12","V13","V14","V15","V16",
        "V17","V18","V19","V20","V21","V22","V23","V24",
        "V25","V26","V27","V28","Amount","Time"
    ]

    for i, name in enumerate(feature_names):
        inputs[name] = cols[i % 4].number_input(name, value=0.0)

    submitted = st.form_submit_button("Analyze Transaction")

# RESULT
if submitted:
    headers = {"api-key": API_KEY}

    res = requests.post(API_URL, json=inputs, headers=headers)

    result = res.json()

    if "error" in result:
        st.error(result["error"])
    else:
        score = result["fraud_score"]
        status = result["status"]

        st.subheader("📊 Result")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Fraud Score", f"{score:.4f}")

        with col2:
            st.metric("Status", status)

        # RISK INDICATOR
        st.subheader("⚠️ Risk Level")

        if score < 0.3:
            st.success("Low Risk Transaction ✅")
        elif score < 0.7:
            st.warning("Medium Risk Transaction ⚠️")
        else:
            st.error("High Risk Transaction 🚨")

        # SIMPLE BAR
        st.progress(float(score))