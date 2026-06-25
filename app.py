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

app = FastAPI(title="Fraud SaaS V3")

# =========================
# USER TABLE
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
# LOAD MODEL
# =========================
rf_model = joblib.load("rf_model.pkl")
scaler = joblib.load("scaler.pkl")


# =========================
# HELPERS
# =========================
def get_db():
    return SessionLocal()


def get_user_by_key(api_key: str):
    db = get_db()
    user = db.query(User).filter(User.api_key == api_key).first()
    db.close()
    return user


# =========================
# HOME
# =========================
@app.get("/")
def home():
    return {"status": "Fraud SaaS API running"}


# =========================
# SIGNUP (FIXED)
# =========================
@app.post("/signup")
def signup(email: str, password: str):

    db = get_db()

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        db.close()
        return {"error": "User already exists"}

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
    db.close()

    return {"api_key": user.api_key}


# =========================
# LOGIN (CRITICAL FIX)
# =========================
@app.post("/login")
def login(email: str, password: str):

    db = get_db()

    user = db.query(User).filter(User.email == email).first()

    db.close()

    if not user or user.password != password:
        return {"error": "Invalid login"}

    return {
        "api_key": user.api_key,
        "plan": user.plan,
        "requests": user.requests
    }


# =========================
# PREDICT (FIXED 30 FEATURES)
# =========================
@app.post("/predict")
def predict(payload: dict, api_key: str = Header(None)):

    user = get_user_by_key(api_key)

    if not user:
        return {"error": "Invalid API key"}

    if user.requests >= user.limit:
        return {"error": "Limit reached"}

    try:
        features = payload.get("features")

        if not features:
            return {"error": "Missing features"}

        values = np.array([features], dtype=float)

        # MUST BE 30 FEATURES
        if values.shape[1] != 30:
            return {
                "error": "Model expects 30 features",
                "received": int(values.shape[1])
            }

        scaled = scaler.transform(values)

        score = rf_model.predict_proba(scaled)[0][1]

        db = get_db()
        user.requests += 1
        db.merge(user)
        db.commit()
        db.close()

        return {
            "fraud_score": float(score),
            "status": "FRAUD" if score > 0.5 else "NORMAL",
            "remaining": user.limit - user.requests
        }

    except Exception as e:
        return {"error": str(e)}


# =========================
# ADMIN STATS
# =========================
@app.get("/admin/stats")
def stats():
    db = get_db()
    users = db.query(User).all()
    db.close()

    return {
        "total_users": len(users),
        "total_requests": sum(u.requests for u in users),
        "total_revenue": sum(u.revenue for u in users)
    }