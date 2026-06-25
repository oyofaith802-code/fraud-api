from fastapi import FastAPI, Header
import joblib
import numpy as np
import pandas as pd
from pydantic import BaseModel

app = FastAPI()

API_KEY = "my_secret_12345"

# Load models
rf_model = joblib.load("rf_model.pkl")
xgb_model = joblib.load("xgb_model.pkl")
scaler = joblib.load("scaler.pkl")


# Input schema (IMPORTANT for correct feature order)
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


@app.post("/predict")
def predict(data: Transaction, api_key: str = Header(None)):

    try:
        # API KEY CHECK
        if api_key != API_KEY:
            return {"error": "Unauthorized: Invalid API Key"}

        # Convert input to DataFrame (VERY IMPORTANT for feature order)
        df = pd.DataFrame([data.dict()])

        # Scale
        df_scaled = scaler.transform(df)

        # Predictions
        rf_prob = rf_model.predict_proba(df_scaled)[0][1]
        xgb_prob = xgb_model.predict_proba(df_scaled)[0][1]

        # Ensemble
        fraud_score = (rf_prob + xgb_prob) / 2
        status = "FRAUD" if fraud_score > 0.5 else "NORMAL"

        return {
            "fraud_score": float(fraud_score),
            "status": status
        }

    except Exception as e:
        return {"error": str(e)}