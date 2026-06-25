from fastapi import FastAPI, Header
import joblib
import pandas as pd
from pydantic import BaseModel
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

app = FastAPI()

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

# Load models
rf_model = joblib.load("rf_model.pkl")
xgb_model = joblib.load("xgb_model.pkl")
scaler = joblib.load("scaler.pkl")

# MUST MATCH TRAINING ORDER
cols = [
    "V1","V2","V3","V4","V5","V6","V7","V8","V9","V10",
    "V11","V12","V13","V14","V15","V16","V17","V18","V19","V20",
    "V21","V22","V23","V24","V25","V26","V27","V28","Amount","Time"
]

# Input schema
class Transaction(BaseModel):
    V1: float; V2: float; V3: float; V4: float; V5: float
    V6: float; V7: float; V8: float; V9: float; V10: float
    V11: float; V12: float; V13: float; V14: float; V15: float
    V16: float; V17: float; V18: float; V19: float; V20: float
    V21: float; V22: float; V23: float; V24: float; V25: float
    V26: float; V27: float; V28: float
    Amount: float
    Time: float


@app.get("/check")
def check():
    return {
        "api_key_loaded": API_KEY
    }


@app.post("/predict")
def predict(data: Transaction, api_key: str = Header(None)):

    try:

        # Check API key
        if not api_key:
            return {
                "error": "No API key provided"
            }

        if api_key.strip() != API_KEY.strip():
            return {
                "error": "Unauthorized",
                "received": api_key,
                "expected": API_KEY
            }

        # Convert input to ordered list
        values = [
            data.V1, data.V2, data.V3, data.V4, data.V5,
            data.V6, data.V7, data.V8, data.V9, data.V10,
            data.V11, data.V12, data.V13, data.V14, data.V15,
            data.V16, data.V17, data.V18, data.V19, data.V20,
            data.V21, data.V22, data.V23, data.V24, data.V25,
            data.V26, data.V27, data.V28,
            data.Amount, data.Time
        ]

        # Convert to numpy array
        input_array = np.array(values).reshape(1, -1)

        # Scale features
        scaled = scaler.transform(input_array)

        # Model predictions
        rf_prob = rf_model.predict_proba(scaled)[0][1]
        xgb_prob = xgb_model.predict_proba(scaled)[0][1]

        # Ensemble score
        fraud_score = (rf_prob + xgb_prob) / 2

        return {
            "fraud_score": float(fraud_score),
            "status": "FRAUD" if fraud_score > 0.5 else "NORMAL"
        }

    except Exception as e:
        return {
            "error": str(e)
        }