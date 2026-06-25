import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Fraud Analytics Dashboard", layout="wide")

API_URL = "https://fraud-api-1d91.onrender.com/predict"
API_KEY = "my_secret_12345"

st.title("🏦 Fraud Detection Analytics Dashboard")

# SESSION STORAGE
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- INPUT ----------------
st.subheader("🔎 New Transaction Analysis")

with st.form("form"):
    cols = st.columns(4)

    feature_names = [
        "V1","V2","V3","V4","V5","V6","V7","V8",
        "V9","V10","V11","V12","V13","V14","V15","V16",
        "V17","V18","V19","V20","V21","V22","V23","V24",
        "V25","V26","V27","V28","Amount","Time"
    ]

    data = {}

    for i, name in enumerate(feature_names):
        data[name] = cols[i % 4].number_input(name, value=0.0)

    submitted = st.form_submit_button("Analyze")

# ---------------- API CALL ----------------
if submitted:
    headers = {"api-key": API_KEY}
    res = requests.post(API_URL, json=data, headers=headers)
    result = res.json()

    if "error" in result:
        st.error(result["error"])
    else:
        score = result["fraud_score"]
        status = result["status"]

        # save history
        st.session_state.history.append({
            "score": score,
            "status": status
        })

        st.success("Analysis Complete")

        col1, col2, col3 = st.columns(3)

        col1.metric("Fraud Score", f"{score:.4f}")
        col2.metric("Status", status)

        if score < 0.3:
            col3.success("LOW RISK")
        elif score < 0.7:
            col3.warning("MEDIUM RISK")
        else:
            col3.error("HIGH RISK")

        st.progress(float(score))

# ---------------- ANALYTICS ----------------
st.subheader("📊 Analytics Overview")

history = st.session_state.history

if len(history) > 0:

    df = pd.DataFrame(history)

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Transactions", len(df))
        st.metric("Fraud Detected", (df["status"] == "FRAUD").sum())

    with col2:
        fraud_rate = (df["status"] == "FRAUD").mean() * 100
        st.metric("Fraud Rate %", f"{fraud_rate:.2f}%")

    # ---------------- CHART 1 ----------------
    st.subheader("📈 Fraud vs Normal Distribution")

    fig1, ax1 = plt.subplots()
    df["status"].value_counts().plot(kind="bar", ax=ax1)
    ax1.set_ylabel("Count")
    st.pyplot(fig1)

    # ---------------- CHART 2 ----------------
    st.subheader("📉 Fraud Score Distribution")

    fig2, ax2 = plt.subplots()
    ax2.hist(df["score"], bins=10)
    ax2.set_xlabel("Fraud Score")
    st.pyplot(fig2)

else:
    st.info("No transactions yet. Run a prediction to see analytics.")