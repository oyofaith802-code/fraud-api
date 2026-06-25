import streamlit as st
import requests
import matplotlib.pyplot as plt

# ✅ YOUR REAL RENDER BACKEND
API = "https://fraud-api-1d91.onrender.com"

st.set_page_config(layout="wide")

# =========================
# 🔐 LOGIN SECTION
# =========================
if "api_key" not in st.session_state:

    st.title("🔐 Fraud SaaS Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            res = requests.post(
                f"{API}/login",
                params={
                    "email": email,
                    "password": password
                }
            ).json()

            if "api_key" in res:
                st.session_state.api_key = res["api_key"]
                st.session_state.email = email
                st.rerun()
            else:
                st.error(res.get("error", "Login failed"))

        except Exception as e:
            st.error(f"API error: {e}")

    st.stop()


# =========================
# 📊 DASHBOARD DATA
# =========================
try:
    data = requests.get(
        f"{API}/user/dashboard",
        params={"api_key": st.session_state.api_key}
    ).json()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()


st.title("💰 Fraud Detection SaaS Dashboard")

# =========================
# 📈 METRICS
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("Plan", data.get("plan", "FREE"))
col2.metric("Used Requests", data.get("requests_used", 0))
col3.metric("Remaining", data.get("remaining", 0))


# =========================
# 📊 USAGE CHART
# =========================
fig, ax = plt.subplots()

ax.bar(
    ["Used", "Remaining"],
    [data.get("requests_used", 0), data.get("remaining", 0)]
)

ax.set_title("API Usage Overview")

st.pyplot(fig)


# =========================
# 🔑 API KEY SECTION
# =========================
st.subheader("🔑 API KEY")
st.code(data.get("api_key", "N/A"))


# =========================
# 🚀 UPGRADE BUTTON (PAYSTACK)
# =========================
st.subheader("💳 Upgrade Plan")

if st.button("🚀 Upgrade to PRO"):

    try:
        res = requests.post(
            f"{API}/paystack/pay",
            json={
                "email": data.get("email"),
                "plan": "pro"
            }
        ).json()

        st.success("Payment initialized")
        st.json(res)

    except Exception as e:
        st.error(f"Upgrade failed: {e}")