from fastapi import FastAPI, Header
import joblib
import numpy as np
from pydantic import BaseModel
import os
import uuid
import requests
from dotenv import load_dotenv

# =========================
# LOAD ENV
# =========================
load_dotenv()

API_KEY = os.getenv("API_KEY")
PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY")
BASE_URL = os.getenv("BASE_URL")

# =========================
# APP INIT
# =========================
app = FastAPI()

# =========================
# LOAD MODELS
# =========================
rf_model = joblib.load("rf_model.pkl")
xgb_model = joblib.load("xgb_model.pkl")
scaler = joblib.load("scaler.pkl")

# =========================
# SIMPLE IN-MEMORY DB
# =========================
USERS = {}

# =========================
# INPUT SCHEMA
# =========================
class Transaction(BaseModel):
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Amount: float
    Time: float


# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {"message": "Fraud API SaaS running 🚀"}


# =========================
# SIGNUP (CREATE USER + API KEY)
# =========================
@app.post("/signup")
def signup(email: str):

    user_id = str(uuid.uuid4())
    api_key = "fk_" + str(uuid.uuid4()).replace("-", "")[:20]

    USERS[user_id] = {
        "email": email,
        "api_key": api_key,
        "plan": "FREE",
        "requests": 0,
        "limit": 5
    }

    return {
        "user_id": user_id,
        "api_key": api_key,
        "plan": "FREE"
    }


# =========================
# PAYSTACK INIT
# =========================
@app.post("/pay")
def pay(email: str):

    url = "https://api.paystack.co/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET}",
        "Content-Type": "application/json"
    }

    data = {
        "email": email,
        "amount": 200000,  # ₦2000
        "callback_url": f"{BASE_URL}/upgrade?email={email}"
    }

    response = requests.post(url, json=data, headers=headers)

    return response.json()


# =========================
# UPGRADE AFTER PAYMENT
# =========================
@app.get("/upgrade")
def upgrade(email: str):

    for user in USERS.values():
        if user["email"] == email:
            user["plan"] = "BASIC"
            user["limit"] = 500

            return {
                "message": "Payment successful 🚀",
                "plan": "BASIC",
                "limit": 500
            }

    return {"error": "User not found"}


# =========================
# PREDICT (SAAS PROTECTED)
# =========================
@app.post("/predict")
def predict(data: Transaction, api_key: str = Header(None)):

    # FIND USER
    user = None
    for u in USERS.values():
        if u["api_key"] == api_key:
            user = u
            break

    if not user:
        return {"error": "Invalid API key"}

    # CHECK LIMIT
    if user["requests"] >= user["limit"]:
        return {"error": "Limit reached. Upgrade plan."}

    try:
        values = [
            data.V1, data.V2, data.V3, data.V4, data.V5,
            data.V6, data.V7, data.V8, data.V9, data.V10,
            data.V11, data.V12, data.V13, data.V14, data.V15,
            data.V16, data.V17, data.V18, data.V19, data.V20,
            data.V21, data.V22, data.V23, data.V24, data.V25,
            data.V26, data.V27, data.V28,
            data.Amount, data.Time
        ]

        # Convert to numpy
        input_array = np.array(values).reshape(1, -1)

        # Scale
        scaled = scaler.transform(input_array)

        # Predict
        rf_prob = rf_model.predict_proba(scaled)[0][1]
        xgb_prob = xgb_model.predict_proba(scaled)[0][1]

        fraud_score = (rf_prob + xgb_prob) / 2

        # Update usage
        user["requests"] += 1

        return {
            "transaction_id": f"TXN_{uuid.uuid4().hex[:8]}",
            "fraud_score": float(fraud_score),
            "status": "FRAUD" if fraud_score > 0.5 else "NORMAL",
            "remaining_calls": user["limit"] - user["requests"]
        }

    except Exception as e:
        return {"error": str(e)}