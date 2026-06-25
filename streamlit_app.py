import streamlit as st
import requests
import matplotlib.pyplot as plt

API = "https://your-render-url.onrender.com"

st.set_page_config(layout="wide")

# ================= LOGIN =================
if "token" not in st.session_state:
    st.title("🚀 Fraud SaaS V4")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(f"{API}/login", params={
            "email": email,
            "password": password
        }).json()

        st.session_state.token = res["token"]
        st.rerun()

    st.stop()

headers = {"Authorization": f"Bearer {st.session_state.token}"}

# ================= ANALYTICS =================
analytics = requests.get(f"{API}/analytics", headers=headers).json()

st.title("📊 Dashboard")

st.metric("Requests", analytics["total_requests"])
st.metric("Avg Score", analytics["avg_score"])

# ================= HEATMAP =================
st.subheader("📈 Usage Heatmap")

fig, ax = plt.subplots()

scores = [x["score"] for x in analytics["heatmap"]]

ax.plot(scores)
st.pyplot(fig)

# ================= BILLING =================
billing = requests.get(f"{API}/billing", headers=headers).json()

st.subheader("🧾 Billing")
st.write(billing)

# ================= PREDICT =================
st.subheader("🧠 Fraud Prediction")

v1 = st.number_input("V1")
v2 = st.number_input("V2")
v3 = st.number_input("V3")
amount = st.number_input("Amount")
time = st.number_input("Time")

if st.button("Predict"):

    res = requests.post(
        f"{API}/predict",
        headers=headers,
        params={
            "V1": v1,
            "V2": v2,
            "V3": v3,
            "Amount": amount,
            "Time": time
        }
    ).json()

    st.write(res)