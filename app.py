from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import pandas as pd
app = FastAPI()

# Load models
rf_model = joblib.load("rf_model.pkl")
xgb_model = joblib.load("xgb_model.pkl")
scaler = joblib.load("scaler.pkl")


# Input schema
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


@app.get("/")
def home():
    return {"message": "Fraud Detection API is running"}
@app.post("/predict")
def predict(data: Transaction):
    try:
        import numpy as np

        features = np.array([[
            data.V1, data.V2, data.V3, data.V4, data.V5,
            data.V6, data.V7, data.V8, data.V9, data.V10,
            data.V11, data.V12, data.V13, data.V14, data.V15,
            data.V16, data.V17, data.V18, data.V19, data.V20,
            data.V21, data.V22, data.V23, data.V24, data.V25,
            data.V26, data.V27, data.V28, data.Amount, data.Time
        ]])

        # SCALE (NO COLUMN NAMES)
        features_scaled = scaler.transform(features)

        # PREDICTION
        rf_prob = rf_model.predict_proba(features_scaled)[0][1]
        xgb_prob = xgb_model.predict_proba(features_scaled)[0][1]

        fraud_score = (rf_prob + xgb_prob) / 2

        status = "FRAUD" if fraud_score > 0.5 else "NORMAL"

        return {
            "fraud_score": float(fraud_score),
            "status": status
        }

    except Exception as e:
        return {"error": str(e)}

        # Create DataFrame with exact column order
        features = pd.DataFrame(values, columns=cols)

        # Scale input
        features_scaled = scaler.transform(features)

        # Predictions
        rf_prob = rf_model.predict_proba(features_scaled)[0][1]
        xgb_prob = xgb_model.predict_proba(features_scaled)[0][1]

        # Ensemble score
        fraud_score = (rf_prob + xgb_prob) / 2

        status = "FRAUD" if fraud_score > 0.5 else "NORMAL"

        return {
            "fraud_score": float(fraud_score),
            "status": status
        }

    except Exception as e:
        return {"error": str(e)}