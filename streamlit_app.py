import streamlit as st
import requests
import matplotlib.pyplot as plt

# =========================
# CONFIG
# =========================
API = "https://fraud-api-1d91.onrender.com"

st.set_page_config(page_title="Fraud SaaS Dashboard", layout="wide")

# =========================
# SAFE REQUEST WRAPPER (IMPORTANT FIX)
# =========================
def safe_post(url, params=None, headers=None):
    try:
        r = requests.post(url, params=params, headers=headers, timeout=20)
        try:
            return r.json()
        except:
            return {"error": "Invalid JSON from server", "raw": r.text}
    except Exception as e:
        return {"error": str(e)}


def safe_get(url):
    try:
        r = requests.get(url, timeout=20)
        try:
            return r.json()
        except:
            return {"error": "Invalid JSON from server", "raw": r.text}
    except Exception as e:
        return {"error": str(e)}


# =========================
# SESSION STATE
# =========================
if "api_key" not in st.session_state:
    st.session_state.api_key = None


# =========================
# AUTH SECTION
# =========================
if st.session_state.api_key is None:

    st.title("🚀 Fraud SaaS V3")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    # ---------------- LOGIN ----------------
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            res = safe_post(f"{API}/login", params={
                "email": email,
                "password": password
            })

            if "api_key" in res:
                st.session_state.api_key = res["api_key"]
                st.success("Login successful 🚀")
                st.rerun()
            else:
                st.error(res.get("detail", res))


    # ---------------- SIGNUP ----------------
    with tab2:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Create Account"):
            res = safe_post(f"{API}/signup", params={
                "email": email,
                "password": password
            })

            if "api_key" in res:
                st.success("Account created 🎉")
                st.write("Your API Key:", res["api_key"])
            else:
                st.error(res)

    st.stop()


# =========================
# DASHBOARD
# =========================
st.title("💰 SaaS Fraud Detection Dashboard")

api_key = st.session_state.api_key

# =========================
# STATS (SAFE)
# =========================
data = safe_get(f"{API}/admin/stats")

if "error" in data:
    st.error("Backend error or API not responding")
    st.stop()


# =========================
# METRICS
# =========================
col1, col2, col3 = st.columns(3)

col1.metric("Total Users", data.get("total_users", 0))
col2.metric("Total Requests", data.get("total_requests", 0))
col3.metric("Revenue", f"${data.get('total_revenue', 0)}")


# =========================
# CHARTS
# =========================
st.subheader("📊 Analytics")

fig, ax = plt.subplots()

ax.bar(
    ["Revenue", "Requests"],
    [data.get("total_revenue", 0), data.get("total_requests", 0)]
)

st.pyplot(fig)


# =========================
# API KEY DISPLAY
# =========================
st.subheader("🔑 Your API Key")
st.code(api_key)


# =========================
# TEST PREDICTION
# =========================
st.subheader("🧪 Test Fraud Prediction")

col1, col2 = st.columns(2)

with col1:
    v1 = st.number_input("V1")
    v2 = st.number_input("V2")
    v3 = st.number_input("V3")

with col2:
    amount = st.number_input("Amount")
    time = st.number_input("Time")

if st.button("Run Prediction"):

    res = safe_post(
        f"{API}/predict",
        params={
            "V1": v1,
            "V2": v2,
            "V3": v3,
            "Amount": amount,
            "Time": time
        },
        headers={"api-key": api_key}
    )

    st.write(res)


# =========================
# UPGRADE
# =========================
st.subheader("🚀 Upgrade Plan")

plan = st.selectbox("Choose Plan", ["daily", "monthly"])

if st.button("Upgrade with Paystack"):

    res = safe_post(f"{API}/paystack/pay", params={
        "email": "user@example.com",
        "plan": plan
    })

    if "data" in res and "authorization_url" in res["data"]:
        st.success("Redirect to payment:")
        st.write(res["data"]["authorization_url"])
    else:
        st.error(res)


# =========================
# LOGOUT
# =========================
if st.button("Logout"):
    st.session_state.api_key = None
    st.rerun()