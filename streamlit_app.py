import streamlit as st
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# =========================

# CONFIG

# =========================

API_URL = "https://fraud-api-1d91.onrender.com/predict"
STATS_URL = "https://fraud-api-1d91.onrender.com/stats"

st.set_page_config(
page_title="Fraud SaaS Dashboard V5",
layout="wide"
)

st.title("🚀 Fraud SaaS Dashboard V5")

# =========================

# SESSION STATE

# =========================

if "history" not in st.session_state:
st.session_state.history = []

# =========================

# API KEY

# =========================

st.sidebar.header("🔑 API Configuration")
api_key = st.sidebar.text_input("Enter API Key", type="default")

st.sidebar.markdown("---")
st.sidebar.info("Use your key from /signup endpoint")

# =========================

# FEATURE INPUTS

# =========================

st.subheader("🧪 Transaction Input (Kaggle Format)")

st.write("Enter V1 - V28 + Amount + Time (30 features total)")

features = []

cols = st.columns(3)

for i in range(28):
with cols[i % 3]:
v = st.number_input(f"V{i+1}", value=0.0, step=0.01)
features.append(v)

amount = st.number_input("Amount", value=0.0, step=0.01)
time = st.number_input("Time", value=0.0, step=0.01)

features.append(amount)
features.append(time)

# =========================

# PREDICT BUTTON

# =========================

if st.button("🚀 Predict Fraud"):

```
if not api_key:
    st.error("Please enter API key")
else:
    try:
        headers = {
            "X-API-Key": api_key
        }

        payload = {
            "features": features
        }

        response = requests.post(API_URL, json=payload, headers=headers)

        try:
            data = response.json()
        except:
            st.error("Server returned invalid response")
            st.code(response.text)
            st.stop()

        if "error" in data:
            st.error(data["error"])
        else:
            score = data["fraud_score"]
            status = data["status"]

            st.success(f"Fraud Score: {score:.4f}")
            st.info(f"Prediction: {status}")

            # =========================
            # EXPLANATION ENGINE
            # =========================
            st.subheader("🧠 Explanation")

            if score > 0.7:
                st.error("🔴 High Risk Transaction")
                st.write("- Very strong anomaly detected")
                st.write("- Pattern deviates from normal behavior")
                st.write("- Likely fraud attempt")

            elif score > 0.3:
                st.warning("🟡 Medium Risk Transaction")
                st.write("- Some unusual patterns detected")
                st.write("- Requires review")

            else:
                st.success("🟢 Low Risk Transaction")
                st.write("- Normal transaction pattern")
                st.write("- No suspicious signals")

            # =========================
            # SAVE HISTORY
            # =========================
            st.session_state.history.append({
                "score": score,
                "status": status
            })

    except Exception as e:
        st.error(f"Request failed: {str(e)}")
```

# =========================

# DASHBOARD ANALYTICS

# =========================

st.divider()
st.header("📊 Analytics Dashboard")

if len(st.session_state.history) > 0:

```
df = pd.DataFrame(st.session_state.history)

total = len(df)
fraud = len(df[df["status"] == "FRAUD"])
normal = len(df[df["status"] == "NORMAL"])

col1, col2, col3 = st.columns(3)

col1.metric("Total Predictions", total)
col2.metric("Fraud Cases", fraud)
col3.metric("Normal Cases", normal)

# =========================
# SCORE TREND
# =========================
st.subheader("📈 Fraud Score Trend")

st.line_chart(df["score"])

# =========================
# PIE CHART SAFE VERSION
# =========================
st.subheader("📊 Fraud Distribution")

if fraud + normal > 0:
    fig, ax = plt.subplots()

    ax.pie(
        [fraud, normal],
        labels=["Fraud", "Normal"],
        autopct="%1.1f%%"
    )

    st.pyplot(fig)
else:
    st.info("No data yet")

# =========================
# RAW DATA
# =========================
st.subheader("📄 Prediction History")
st.dataframe(df)
```

else:
st.info("Run predictions to generate analytics")
