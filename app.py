from fastapi import FastAPI, Header
import joblib
import numpy as np
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")

app = FastAPI()

# Load models
rf_model = joblib.load("rf_model.pkl")
xgb_model = joblib.load("xgb_model.pkl")
scaler = joblib.load("scaler.pkl")


# Input schema (must match training order)
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


# Check API key status (debug)
@app.get("/check")
def check():
    return {
        "api_key_loaded": bool(API_KEY)
    }


# MAIN PREDICTION ENDPOINT
@app.post("/predict")
def predict(data: Transaction, api_key: str = Header(None)):

    try:
        # ---------------------------
        # 1. API KEY VALIDATION
        # ---------------------------
        if not API_KEY:
            return {"error": "Server API key not set"}

        if not api_key or api_key.strip() != API_KEY.strip():
            return {"error": "Unauthorized"}

        # ---------------------------
        # 2. CONVERT INPUT
        # ---------------------------
        values = [
            data.V1, data.V2, data.V3, data.V4, data.V5,
            data.V6, data.V7, data.V8, data.V9, data.V10,
            data.V11, data.V12, data.V13, data.V14, data.V15,
            data.V16, data.V17, data.V18, data.V19, data.V20,
            data.V21, data.V22, data.V23, data.V24, data.V25,
            data.V26, data.V27, data.V28,
            data.Amount, data.Time
        ]

        input_array = np.array(values).reshape(1, -1)

        # ---------------------------
        # 3. SCALE INPUT
        # ---------------------------
        scaled = scaler.transform(input_array)

        # ---------------------------
        # 4. MODEL PREDICTIONS
        # ---------------------------
        rf_prob = rf_model.predict_proba(scaled)[0][1]
        xgb_prob = xgb_model.predict_proba(scaled)[0][1]

        fraud_score = (rf_prob + xgb_prob) / 2

        # ---------------------------
        # 5. RULES ENGINE (BANK LOGIC)
        # ---------------------------
        if data.Amount > 10000:
            fraud_score = min(fraud_score + 0.15, 1)

        if data.Time < 5000:
            fraud_score = min(fraud_score + 0.05, 1)

        if data.V14 < -2:
            fraud_score = min(fraud_score + 0.1, 1)

        # ---------------------------
        # 6. DECISION ENGINE
        # ---------------------------
        if fraud_score < 0.3:
            risk_level = "LOW"
            decision = "APPROVE"
        elif fraud_score < 0.7:
            risk_level = "MEDIUM"
            decision = "REVIEW"
        else:
            risk_level = "HIGH"
            decision = "BLOCK"

        # ---------------------------
        # 7. RESPONSE
        # ---------------------------
        return {
            "transaction_id": "TXN_" + str(np.random.randint(1000000, 9999999)),
            "fraud_score": float(fraud_score),
            "risk_level": risk_level,
            "decision": decision,
            "status": "SUCCESS"
        }

    except Exception as e:
        return {
            "error": str(e)
        }