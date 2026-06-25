import os
import uuid
import time
import logging
import numpy as np
import joblib

from fastapi import FastAPI, Header, HTTPException
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import requests

# =========================
# LOGGING (IMPORTANT FOR RENDER DEBUG)
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fraud-saas")

logger.info("🚀 Starting Fraud API SaaS...")

# =========================
# LOAD ENV
# =========================
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")
PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET_KEY")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# =========================
# DB SETUP
# =========================
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# =========================
# USER MODEL
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)

    api_key = Column(String, unique=True)

    plan = Column(String, default="FREE")
    requests = Column(Integer, default=0)
    limit = Column(Integer, default=2)

    revenue = Column(Float, default=0.0)

Base.metadata.create_all(bind=engine)

# =========================
# FASTAPI APP
# =========================
app = FastAPI(title="Fraud API SaaS v3")

@app.get("/")
def home():
    return {"status": "Fraud API Running"}

# =========================
# SAFE MODEL LOADING
# =========================
MODEL_PATH = "rf_model.pkl"
SCALER_PATH = "scaler.pkl"

rf_model = None
scaler = None

try:
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        rf_model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        logger.info("✅ ML model loaded successfully")
    else:
        logger.warning("⚠️ ML model files missing — running in SAFE MODE")
except Exception as e:
    logger.error(f"Model loading failed: {e}")

# =========================
# HELPERS
# =========================
def get_user(api_key: str):
    db = SessionLocal()
    return db.query(User).filter(User.api_key == api_key).first()

# =========================
# SIGNUP
# =========================
@app.post("/signup")
def signup(email: str, password: str):
    db = SessionLocal()

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(400, "User already exists")

    user = User(
        id=str(uuid.uuid4()),
        email=email,
        password=password,
        api_key="fk_" + uuid.uuid4().hex[:20],
        plan="FREE",
        requests=0,
        limit=2
    )

    db.add(user)
    db.commit()

    return {
        "message": "Account created",
        "api_key": user.api_key
    }

# =========================
# LOGIN
# =========================
@app.post("/login")
def login(email: str, password: str):
    db = SessionLocal()

    user = db.query(User).filter(
        User.email == email,
        User.password == password
    ).first()

    if not user:
        raise HTTPException(401, "Invalid login")

    return {
        "api_key": user.api_key,
        "plan": user.plan,
        "requests": user.requests
    }

# =========================
# PREDICT (SAFE + PRODUCTION)
# =========================
@app.post("/predict")
def predict(
    V1: float,
    V2: float,
    V3: float,
    Amount: float,
    Time: float,
    api_key: str = Header(None)
):

    user = get_user(api_key)

    if not user:
        raise HTTPException(401, "Invalid API key")

    if user.requests >= user.limit:
        return {
            "error": "Limit reached. Upgrade required."
        }

    if rf_model is None or scaler is None:
        return {
            "error": "Model not loaded on server"
        }

    start = time.time()

    X = np.array([[V1, V2, V3, Amount, Time]])
    X = scaler.transform(X)

    score = rf_model.predict_proba(X)[0][1]

    user.requests += 1

    db = SessionLocal()
    db.add(user)
    db.commit()

    return {
        "fraud_score": float(score),
        "status": "FRAUD" if score > 0.5 else "NORMAL",
        "remaining": user.limit - user.requests,
        "latency_ms": round((time.time() - start) * 1000, 2)
    }

# =========================
# PAYSTACK INIT
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
# PAYSTACK CALLBACK
# =========================
@app.get("/paystack/callback")
def callback(reference: str):

    res = requests.get(
        f"https://api.paystack.co/transaction/verify/{reference}",
        headers={"Authorization": f"Bearer {PAYSTACK_SECRET}"}
    ).json()

    if res.get("data", {}).get("status") == "success":

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
# ADMIN STATS
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