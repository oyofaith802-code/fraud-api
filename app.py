import streamlit as st
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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

# API KEY INPUT

# =========================

api_key = st.text_input("🔑 API Key")

st.divider()

# =========================

# FEATURE INPUTS (30 FEATURES)

# =========================

st.subheader("🧪 Transaction Features (V1 - V28 + Amount + Time)")

features = []

cols = st.columns(3)

for i in range(30):
with cols[i % 3]:
value = st.number_input(f"F{i+1}", value=0.0, step=0.01)
features.append(value)

# =========================

# PREDICTION BUTTON

# =========================

if st.button("Predict Fraud Risk"):

```
if not api_key:
    st.error("API key required")
else:
    try:
        headers = {
            "X-API-Key": api_key
        }

        payload = {
            "features": features
        }

        res = requests.post(API_URL, json=payload, headers=headers)

        try:
            data = res.json()
        except:
            st.error("Server returned invalid response")
            st.write(res.text)
            st.stop()

        if "error" in data:
            st.error(data["error"])
        else:
            score = data["fraud_score"]
            status = data["status"]

            st.success(f"Score: {score:.4f}")
            st.info(f"Status: {status}")

            if status == "FRAUD":
                st.error("""
```

High Risk Transaction

Possible reasons:

* Suspicious pattern detected
* Outlier behavior
* High anomaly score
  """)
  else:
  st.success("""
  Low Risk Transaction

Possible reasons:

* Normal spending pattern
* No anomaly detected
  """)

  ```
            st.session_state.history.append({
                "score": score,
                "status": status
            })

    except Exception as e:
        st.error(str(e))
  ```

# =========================

# DASHBOARD ANALYTICS

# =========================

st.divider()
st.header("📊 Dashboard Analytics")

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
# LINE CHART
# =========================
st.subheader("📈 Risk Score Trend")
st.line_chart(df["score"])

# =========================
# PIE CHART (FIXED ZERO ERROR)
# =========================
st.subheader("📊 Distribution")

labels = ["Fraud", "Normal"]
values = [fraud, normal]

if sum(values) > 0:
    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%")
    st.pyplot(fig)
else:
    st.info("No data yet")
```

else:
st.info("Run predictions to see analytics")
