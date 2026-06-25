import os
import uuid
import jwt
import time
import json
import numpy as np
import pandas as pd
import requests

from datetime import datetime, timedelta

from fastapi import FastAPI, Header, HTTPException, Depends
from sqlalchemy import create_engine, Column, String, Integer, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from dotenv import load_dotenv

import joblib

# ================= ENV =================
load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET", "secret123")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")
PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY", "")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# ================= APP =================
app = FastAPI(title="Fraud SaaS V4 - Stripe Level")

# ================= DB =================
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================= USER =================
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)

    plan = Column(String, default="FREE")
    requests = Column(Integer, default=0)
    limit = Column(Integer, default=5)

    revenue = Column(Float, default=0)
    usage_log = Column(Text, default="[]")

Base.metadata.create_all(bind=engine)

# ================= LOAD MODEL =================
rf_model = joblib.load("rf_model.pkl")
scaler = joblib.load("scaler.pkl")

# ================= JWT =================
def create_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except:
        return None

# ================= RATE LIMIT (STRIPE STYLE) =================
def rate_limit(user: User):
    if user.requests >= user.limit:
        raise HTTPException(429, "Rate limit exceeded")

# ================= SIGNUP =================
@app.post("/signup")
def signup(email: str, password: str, db: Session = Depends(get_db)):

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "User exists")

    user = User(
        id=str(uuid.uuid4()),
        email=email,
        password=password
    )

    db.add(user)
    db.commit()

    return {"message": "created"}

# ================= LOGIN (JWT) =================
@app.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(
        User.email == email,
        User.password == password
    ).first()

    if not user:
        raise HTTPException(401, "Invalid login")

    token = create_token(user.id)

    return {
        "token": token,
        "plan": user.plan
    }

# ================= GET USER FROM TOKEN =================
def get_user(db, token):
    data = verify_token(token)
    if not data:
        return None
    return db.query(User).filter(User.id == data["user_id"]).first()

# ================= PREDICT + EXPLAINABLE AI =================
@app.post("/predict")
def predict(V1: float, V2: float, V3: float, Amount: float, Time: float,
            authorization: str = Header(None),
            db: Session = Depends(get_db)):

    token = authorization.replace("Bearer ", "")
    user = get_user(db, token)

    if not user:
        raise HTTPException(401, "Invalid token")

    rate_limit(user)

    x = np.array([[V1, V2, V3, Amount, Time]])
    x = scaler.transform(x)

    score = float(rf_model.predict_proba(x)[0][1])

    reasons = []
    if Amount > 1000:
        reasons.append("High transaction value")
    if V3 < -2:
        reasons.append("Anomaly pattern detected")
    if score > 0.7:
        reasons.append("High model confidence fraud")

    user.requests += 1

    logs = json.loads(user.usage_log)
    logs.append({
        "time": str(datetime.utcnow()),
        "score": score
    })
    user.usage_log = json.dumps(logs)

    db.commit()

    return {
        "fraud_score": score,
        "status": "FRAUD" if score > 0.5 else "NORMAL",
        "reasons": reasons
    }

# ================= ANALYTICS =================
@app.get("/analytics")
def analytics(authorization: str = Header(None),
              db: Session = Depends(get_db)):

    token = authorization.replace("Bearer ", "")
    user = get_user(db, token)

    logs = json.loads(user.usage_log)

    df = pd.DataFrame(logs)

    return {
        "total_requests": user.requests,
        "avg_score": float(df["score"].mean()) if len(df) > 0 else 0,
        "heatmap": logs
    }

# ================= BILLING HISTORY =================
@app.get("/billing")
def billing(authorization: str = Header(None),
            db: Session = Depends(get_db)):

    token = authorization.replace("Bearer ", "")
    user = get_user(db, token)

    return {
        "plan": user.plan,
        "requests": user.requests,
        "limit": user.limit,
        "revenue": user.revenue
    }

# ================= ADMIN =================
@app.get("/admin")
def admin(db: Session = Depends(get_db)):

    users = db.query(User).all()

    return {
        "users": len(users),
        "requests": sum(u.requests for u in users),
        "revenue": sum(u.revenue for u in users)
    }