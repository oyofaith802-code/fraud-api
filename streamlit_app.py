import streamlit as st
import requests

# =========================
# CONFIG
# =========================
API = "https://fraud-api-1d91.onrender.com"

st.set_page_config(page_title="Fraud SaaS", layout="wide")


# =========================
# SAFE JSON
# =========================
def safe_json(res):
    try:
        return res.json()
    except:
        return {"error": res.text}


# =========================
# SESSION
# =========================
if "api_key" not in st.session_state:
    st.session_state.api_key = None


# =========================
# AUTH PAGE
# =========================
if not st.session_state.api_key:

    st.title("🚀 Fraud SaaS V1")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    # LOGIN
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            res = safe_json(requests.post(f"{API}/login", params={
                "email": email,
                "password": password
            }))

            if "api_key" in res:
                st.session_state.api_key = res["api_key"]
                st.success("Login successful")
                st.rerun()
            else:
                st.error(res)

    # SIGNUP
    with tab2:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pass")

        if st.button("Create Account"):
            res = safe_json(requests.post(f"{API}/signup", params={
                "email": email,
                "password": password
            }))

            if "api_key" in res:
                st.success("Account created")
                st.code(res["api_key"])
            else:
                st.error(res)

    st.stop()


# =========================
# DASHBOARD
# =========================
st.title("💰 Fraud Detection SaaS Dashboard")

api_key = st.session_state.api_key


# =========================
# STATS
# =========================
stats = safe_json(requests.get(f"{API}/admin/stats"))

if "error" not in stats:
    col1, col2, col3 = st.columns(3)

    col1.metric("Users", stats["total_users"])
    col2.metric("Requests", stats["total_requests"])
    col3.metric("Revenue", stats["total_revenue"])


# =========================
# PREDICTION
# =========================
st.subheader("🧪 Fraud Prediction")

c1, c2 = st.columns(2)

with c1:
    V1 = st.number_input("V1")
    V2 = st.number_input("V2")
    V3 = st.number_input("V3")

with c2:
    Amount = st.number_input("Amount")
    Time = st.number_input("Time")

if st.button("Predict"):
    res = safe_json(requests.post(
        f"{API}/predict",
        headers={"api-key": api_key},
        params={
            "V1": V1,
            "V2": V2,
            "V3": V3,
            "Amount": Amount,
            "Time": Time
        }
    ))

    st.write(res)


# =========================
# LOGOUT
# =========================
if st.button("Logout"):
    st.session_state.api_key = None
    st.rerun()