from fastapi import FastAPI, Header, HTTPException
import joblib
import numpy as np   
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
API_KEY = "my_secret_12345"
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
def predict(data: Transaction, api_key: str = Header(None)):
    
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")

    try:
        input_data = np.array([list(data.dict().values())])
        scaled_data = scaler.transform(input_data)

        prediction = model.predict_proba(scaled_data)[0][1]

        return {
            "fraud_score": float(prediction),
            "status": "FRAUD" if prediction > 0.5 else "NORMAL"
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