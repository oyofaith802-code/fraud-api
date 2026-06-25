import os
import uuid
import numpy as np
from datetime import datetime

from fastapi import FastAPI, Header
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime
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

app = FastAPI(title="Fraud SaaS V6")

# ======================
# TABLES
# ======================
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    api_key = Column(String, unique=True)
    requests = Column(Integer, default=0)
    limit = Column(Integer, default=50)


class FraudHistory(Base):
    __tablename__ = "fraud_history"

    id = Column(String, primary_key=True)
    api_key = Column(String)
    score = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(String, primary_key=True)
    api_key = Column(String)
    endpoint = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)

# ======================
# MODEL
# ======================
rf_model = joblib.load("rf_model.pkl")
scaler = joblib.load("scaler.pkl")


def db():
    return SessionLocal()


def get_user(api_key: str):
    session = db()
    user = session.query(User).filter(User.api_key == api_key).first()
    session.close()
    return user


# ======================
# HOME
# ======================
@app.get("/")
def home():
    return {"status": "Fraud SaaS V6 running"}


# ======================
# SIGNUP
# ======================
@app.post("/signup")
def signup(email: str, password: str):
    session = db()

    if session.query(User).filter(User.email == email).first():
        session.close()
        return {"error": "User exists"}

    user = User(
        id=str(uuid.uuid4()),
        email=email,
        password=password,
        api_key="fk_" + uuid.uuid4().hex[:20]
    )

    session.add(user)
    session.commit()
    session.close()

    return {"api_key": user.api_key}


# ======================
# LOGIN
# ======================
@app.post("/login")
def login(email: str, password: str):
    session = db()
    user = session.query(User).filter(User.email == email).first()
    session.close()

    if not user or user.password != password:
        return {"error": "Invalid login"}

    return {"api_key": user.api_key}


# ======================
# PREDICT (FIXED 30 FEATURES)
# ======================
@app.post("/predict")
def predict(payload: dict, api_key: str = Header(None, alias="X-API-Key")):

    user = get_user(api_key)

    if not user:
        return {"error": "Invalid API key"}

    features = payload.get("features")

    if not features or len(features) != 30:
        return {"error": "Need 30 features"}

    try:
        arr = np.array([features], dtype=float)
        scaled = scaler.transform(arr)

        score = rf_model.predict_proba(scaled)[0][1]
        status = "FRAUD" if score > 0.5 else "NORMAL"

        session = db()
        user.requests += 1
        session.merge(user)

        session.add(FraudHistory(
            id=str(uuid.uuid4()),
            api_key=api_key,
            score=float(score),
            status=status
        ))

        session.add(UsageLog(
            id=str(uuid.uuid4()),
            api_key=api_key,
            endpoint="/predict"
        ))

        session.commit()
        session.close()

        return {
            "fraud_score": float(score),
            "status": status,
            "remaining": user.limit - user.requests
        }

    except Exception as e:
        return {"error": str(e)}


# ======================
# STATS
# ======================
@app.get("/stats")
def stats(api_key: str):

    session = db()

    usage = session.query(UsageLog).filter(UsageLog.api_key == api_key).all()
    history = session.query(FraudHistory).filter(FraudHistory.api_key == api_key).all()

    session.close()

    fraud = len([h for h in history if h.status == "FRAUD"])
    normal = len([h for h in history if h.status == "NORMAL"])

    return {
        "total_requests": len(usage),
        "fraud_cases": fraud,
        "normal_cases": normal
    }