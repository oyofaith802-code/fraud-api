from fastapi import FastAPI, Header
import joblib
import pandas as pd
from pydantic import BaseModel

app = FastAPI()

API_KEY = "my_secret_12345"

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


@app.post("/predict")
def predict(data: Transaction, api_key: str = Header(None)):

    try:
        if api_key != API_KEY:
            return {"error": "Unauthorized: Invalid API Key"}

        # STEP 1: convert to dict
        input_dict = data.dict()

        # STEP 2: FORCE correct column order
        df = pd.DataFrame([[input_dict[col] for col in cols]], columns=cols)

        # STEP 3: scale
        df_scaled = scaler.transform(df)

        # STEP 4: predict
        rf_prob = rf_model.predict_proba(df_scaled)[0][1]
        xgb_prob = xgb_model.predict_proba(df_scaled)[0][1]

        fraud_score = (rf_prob + xgb_prob) / 2
        status = "FRAUD" if fraud_score > 0.5 else "NORMAL"

        return {
            "fraud_score": float(fraud_score),
            "status": status
        }

    except Exception as e:
        return {"error": str(e)}