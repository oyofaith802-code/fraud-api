from fastapi import FastAPI, Header
import joblib
import numpy as np
import os
import requests
import uuid
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from database import SessionLocal, User, init_db

load_dotenv()
init_db()

app = FastAPI()

# ENV
API_KEY = os.getenv("API_KEY")
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
BASE_URL = os.getenv("BASE_URL")

# MODELS
rf_model = joblib.load("rf_model.pkl")
xgb_model = joblib.load("xgb_model.pkl")
scaler = joblib.load("scaler.pkl")


# -------------------------
# CREATE USER (SIGNUP)
# -------------------------
@app.post("/signup")
def signup(email: str):

    db = SessionLocal()

    user = User(
        id=str(uuid.uuid4()),
        email=email,
        api_key="fk_" + uuid.uuid4().hex[:20],
        plan="FREE",
        requests=0,
        limit=5,
        revenue=0
    )

    db.add(user)
    db.commit()

    return {
        "email": email,
        "api_key": user.api_key,
        "plan": "FREE"
    }


# -------------------------
# GET USER
# -------------------------
def get_user(api_key, db):
    return db.query(User).filter(User.api_key == api_key).first()


# -------------------------
# PREDICT (MONETIZED API)
# -------------------------
@app.post("/predict")
def predict(
    V1: float, V2: float, V3: float, V4: float, V5: float,
    V6: float, V7: float, V8: float, V9: float, V10: float,
    V11: float, V12: float, V13: float, V14: float, V15: float,
    V16: float, V17: float, V18: float, V19: float, V20: float,
    V21: float, V22: float, V23: float, V24: float, V25: float,
    V26: float, V27: float, V28: float,
    Amount: float,
    Time: float,
    api_key: str = Header(None)
):

    db = SessionLocal()
    user = get_user(api_key, db)

    if not user:
        return {"error": "Invalid API key"}

    if user.requests >= user.limit:
        return {"error": "Free limit reached"}

    values = [
        V1,V2,V3,V4,V5,V6,V7,V8,V9,V10,
        V11,V12,V13,V14,V15,V16,V17,V18,V19,V20,
        V21,V22,V23,V24,V25,V26,V27,V28,
        Amount,Time
    ]

    arr = np.array(values).reshape(1, -1)
    scaled = scaler.transform(arr)

    score = (rf_model.predict_proba(scaled)[0][1] +
             xgb_model.predict_proba(scaled)[0][1]) / 2

    user.requests += 1
    db.commit()

    return {
        "fraud_score": float(score),
        "status": "FRAUD" if score > 0.5 else "NORMAL",
        "remaining": user.limit - user.requests
    }


# -------------------------
# PAYSTACK PAYMENT INIT
# -------------------------
@app.post("/paystack/pay")
def paystack_pay(email: str, plan: str):

    amount_map = {
        "basic": 2000,
        "pro": 5000,
        "premium": 10000
    }

    amount = amount_map.get(plan, 2000) * 100

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


# -------------------------
# PAYSTACK CALLBACK
# -------------------------
@app.get("/paystack/callback")
def paystack_callback(reference: str):

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

        return {"status": "success", "upgraded": True}

    return {"status": "failed"}


# -------------------------
# ADMIN STATS
# -------------------------
@app.get("/admin/stats")
def stats():

    db = SessionLocal()
    users = db.query(User).all()

    return {
        "total_users": len(users),
        "total_requests": sum(u.requests for u in users),
        "total_revenue": sum(u.revenue for u in users)
    }