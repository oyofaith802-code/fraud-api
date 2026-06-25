import os
import uuid
import numpy as np
from fastapi import FastAPI, HTTPException, Header
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import joblib

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

app = FastAPI(title="Fraud SaaS API")

# =========================
# LOAD MODEL
# =========================
rf_model = joblib.load("rf_model.pkl")
scaler = joblib.load("scaler.pkl")

# =========================
# USER FETCH
# =========================
def get_user_by_key(api_key: str):
    db = SessionLocal()
    user = db.execute(
        f"SELECT * FROM users WHERE api_key='{api_key}'"
    ).fetchone()
    db.close()
    return user


# =========================
# PREDICT (FIXED)
# =========================
@app.post("/predict")
def predict(payload: dict, api_key: str = Header(None, alias="api-key")):

    user = get_user_by_key(api_key)

    if not user:
        return {"error": "Invalid API key"}

    if user.requests >= user.limit:
        return {"error": "Limit reached"}

    try:
        features = payload.get("features")

        if not features:
            return {"error": "No features provided"}

        # FORCE NUMPY ARRAY
        values = np.array([features], dtype=float)

        # MUST BE 30 FEATURES
        if values.shape[1] != 30:
            return {
                "error": "Model expects 30 features",
                "received": values.shape[1]
            }

        scaled = scaler.transform(values)

        score = rf_model.predict_proba(scaled)[0][1]

        db = SessionLocal()
        db.execute(
            f"UPDATE users SET requests = requests + 1 WHERE api_key='{api_key}'"
        )
        db.commit()
        db.close()

        return {
            "fraud_score": float(score),
            "status": "FRAUD" if score > 0.5 else "NORMAL",
            "remaining": user.limit - user.requests
        }

    except Exception as e:
        return {"error": str(e)}