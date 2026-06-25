import os
import uuid
import random
import numpy as np
import joblib
import requests

from fastapi import FastAPI, Header
from dotenv import load_dotenv

from database import SessionLocal, User, init_db

# ---------------- INIT ----------------
load_dotenv()
init_db()

app = FastAPI()

# ---------------- ENV ----------------
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
BASE_URL = os.getenv("BASE_URL")

# ---------------- MODELS ----------------
rf_model = joblib.load("rf_model.pkl")
scaler = joblib.load("scaler.pkl")

try:
    xgb_model = joblib.load("xgb_model.pkl")
    HAS_XGB = True
except:
    HAS_XGB = False


# =========================================================
# SIGNUP (creates account + sends verification code)
# =========================================================
@app.post("/signup")
def signup(email: str, password: str):

    db = SessionLocal()

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return {"error": "User already exists"}

    code = random.randint(100000, 999999)

    user = User(
        id=str(uuid.uuid4()),
        email=email,
        password=password,
        api_key="fk_" + uuid.uuid4().hex[:20],
        verification_code=code,
        verified=0,
        plan="FREE",
        requests=0,
        limit=2,
        revenue=0
    )

    db.add(user)
    db.commit()

    # TEMP EMAIL (replace with SendGrid later)
    print(f"EMAIL VERIFICATION CODE FOR {email}: {code}")

    return {
        "message": "Signup successful. Check email for verification code"
    }


# =========================================================
# VERIFY EMAIL
# =========================================================
@app.post("/verify")
def verify(email: str, code: int):

    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"error": "User not found"}

    if user.verification_code != code:
        return {"error": "Invalid verification code"}

    user.verified = 1
    db.commit()

    return {"status": "Email verified successfully"}


# =========================================================
# LOGIN
# =========================================================
@app.post("/login")
def login(email: str, password: str):

    db = SessionLocal()

    user = db.query(User).filter(
        User.email == email,
        User.password == password
    ).first()

    if not user:
        return {"error": "Invalid credentials"}

    if user.verified == 0:
        return {"error": "Email not verified"}

    return {
        "api_key": user.api_key,
        "plan": user.plan
    }


# =========================================================
# FRAUD PREDICTION API (MAIN PRODUCT)
# =========================================================
@app.post("/predict")
def predict(
    V1: float, V2: float, V3: float,
    Amount: float, Time: float,
    api_key: str = Header(None)
):

    db = SessionLocal()

    user = db.query(User).filter(User.api_key == api_key).first()

    if not user:
        return {"error": "Invalid API key"}

    if user.verified == 0:
        return {"error": "Email not verified"}

    if user.requests >= user.limit:
        return {"error": "Free limit reached. Upgrade required"}

    # MODEL INPUT
    arr = np.array([[V1, V2, V3, Amount, Time]])
    scaled = scaler.transform(arr)

    rf_score = rf_model.predict_proba(scaled)[0][1]

    if HAS_XGB:
        xgb_score = xgb_model.predict_proba(scaled)[0][1]
        score = (rf_score + xgb_score) / 2
    else:
        score = rf_score

    user.requests += 1
    db.commit()

    return {
        "fraud_score": float(score),
        "status": "FRAUD" if score > 0.5 else "NORMAL",
        "remaining": user.limit - user.requests
    }


# =========================================================
# PAYSTACK PAYMENT INIT (DAILY / MONTHLY)
# =========================================================
@app.post("/paystack/pay")
def paystack_pay(email: str, plan: str):

    prices = {
        "daily": 500,
        "monthly": 5000
    }

    amount = prices.get(plan, 5000) * 100

    url = "https://api.paystack.co/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "email": email,
        "amount": amount,
        "callback_url": f"{BASE_URL}/paystack/callback"
    }

    res = requests.post(url, json=data, headers=headers)

    return res.json()


# =========================================================
# PAYSTACK CALLBACK (AUTO UPGRADE)
# =========================================================
@app.get("/paystack/callback")
def callback(reference: str):

    url = f"https://api.paystack.co/transaction/verify/{reference}"

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }

    res = requests.get(url, headers=headers).json()

    if res["data"]["status"] == "success":

        email = res["data"]["customer"]["email"]
        amount = res["data"]["amount"]

        db = SessionLocal()
        user = db.query(User).filter(User.email == email).first()

        if user:
            user.plan = "PRO"
            user.limit = 1000
            user.revenue += amount / 100
            db.commit()

        return {"status": "UPGRADED"}

    return {"status": "FAILED"}


# =========================================================
# ADMIN DASHBOARD STATS
# =========================================================
@app.get("/admin/stats")
def admin():

    db = SessionLocal()
    users = db.query(User).all()

    return {
        "total_users": len(users),
        "total_requests": sum(u.requests for u in users),
        "total_revenue": sum(u.revenue for u in users)
    }