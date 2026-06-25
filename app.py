import os
import uuid
import numpy as np
import joblib
import requests

from fastapi import FastAPI, Header, HTTPException
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# =========================
# INIT
# =========================
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./local.db"
PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# =========================
# APP
# =========================
app = FastAPI(title="Fraud SaaS API")

@app.get("/")
def home():
    return {"status": "running", "service": "Fraud SaaS API"}

# =========================
# DB
# =========================
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    api_key = Column(String, unique=True)

    plan = Column(String, default="FREE")
    requests = Column(Integer, default=0)
    limit = Column(Integer, default=3)

    revenue = Column(Float, default=0)

Base.metadata.create_all(bind=engine)

# =========================
# SAFE MODEL LOADING (NO CRASH)
# =========================
try:
    rf_model = joblib.load("rf_model.pkl")
    scaler = joblib.load("scaler.pkl")
except Exception as e:
    rf_model = None
    scaler = None
    print("⚠️ Model not loaded:", e)

# =========================
# HELPERS
# =========================
def get_user(api_key: str):
    db = SessionLocal()
    return db.query(User).filter(User.api_key == api_key).first()

# =========================
# AUTH
# =========================
@app.post("/signup")
def signup(email: str, password: str):
    db = SessionLocal()

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="User exists")

    user = User(
        id=str(uuid.uuid4()),
        email=email,
        password=password,
        api_key="fk_" + uuid.uuid4().hex[:24],
        plan="FREE",
        limit=3
    )

    db.add(user)
    db.commit()

    return {"message": "created", "api_key": user.api_key}


@app.post("/login")
def login(email: str, password: str):
    db = SessionLocal()

    user = db.query(User).filter(
        User.email == email,
        User.password == password
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid login")

    return {
        "api_key": user.api_key,
        "plan": user.plan,
        "requests": user.requests
    }

# =========================
# PREDICTION API
# =========================
@app.post("/predict")
def predict(
    V1: float, V2: float, V3: float,
    Amount: float, Time: float,
    api_key: str = Header(None)
):
    user = get_user(api_key)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if user.requests >= user.limit:
        return {"error": "limit reached"}

    if not rf_model or not scaler:
        return {"error": "model not available"}

    X = np.array([[V1, V2, V3, Amount, Time]])
    X = scaler.transform(X)

    score = rf_model.predict_proba(X)[0][1]

    user.requests += 1

    db = SessionLocal()
    db.merge(user)
    db.commit()

    return {
        "fraud_score": float(score),
        "status": "FRAUD" if score > 0.5 else "NORMAL",
        "remaining": user.limit - user.requests
    }

# =========================
# PAYSTACK PAYMENT
# =========================
@app.post("/paystack/pay")
def paystack_pay(email: str, plan: str):

    prices = {
        "daily": 2000,
        "monthly": 10000
    }

    amount = prices.get(plan, 2000) * 100

    res = requests.post(
        "https://api.paystack.co/transaction/initialize",
        headers={
            "Authorization": f"Bearer {PAYSTACK_SECRET}",
            "Content-Type": "application/json"
        },
        json={
            "email": email,
            "amount": amount,
            "callback_url": f"{BASE_URL}/paystack/callback"
        }
    )

    return res.json()

# =========================
# PAYSTACK CALLBACK (AUTO UPGRADE)
# =========================
@app.get("/paystack/callback")
def callback(reference: str):

    res = requests.get(
        f"https://api.paystack.co/transaction/verify/{reference}",
        headers={"Authorization": f"Bearer {PAYSTACK_SECRET}"}
    ).json()

    if res["data"]["status"] == "success":

        email = res["data"]["customer"]["email"]
        amount = res["data"]["amount"] / 100

        db = SessionLocal()
        user = db.query(User).filter(User.email == email).first()

        if user:
            user.plan = "PRO"
            user.limit = 1000
            user.revenue += amount
            db.commit()

        return {"status": "upgraded"}

    return {"status": "failed"}

# =========================
# ADMIN DASHBOARD API
# =========================
@app.get("/admin/stats")
def stats():
    db = SessionLocal()
    users = db.query(User).all()

    return {
        "total_users": len(users),
        "total_requests": sum(u.requests for u in users),
        "total_revenue": sum(u.revenue for u in users)
    }