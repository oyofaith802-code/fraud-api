import os
import uuid
import numpy as np
from fastapi import FastAPI, HTTPException, Header
from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import joblib
from fastapi import Header
api_key: str = Header(None)

# ======================
# LOAD ENV
# ======================
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./local.db")

# ======================
# DB SETUP
# ======================
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ======================
# USER MODEL
# ======================
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

# ======================
# APP
# ======================
app = FastAPI(title="Fraud SaaS V3")

@app.get("/")
def home():
    return {"status": "Fraud SaaS API Running"}

# ======================
# RESET DB (DEBUG ONLY)
# ======================
@app.get("/reset-db")
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return {"status": "db reset done"}

# ======================
# LOAD ML MODEL
# ======================
rf_model = joblib.load("rf_model.pkl")
scaler = joblib.load("scaler.pkl")

# ======================
# HELPERS
# ======================
def get_user(api_key: str):
    db = SessionLocal()
    return db.query(User).filter(User.api_key == api_key).first()

# ======================
# SIGNUP
# ======================
@app.post("/signup")
def signup(email: str, password: str):
    db = SessionLocal()

    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return {"error": "User already exists"}

        user = User(
            id=str(uuid.uuid4()),
            email=email,
            password=password,
            api_key="fk_" + uuid.uuid4().hex[:20],
            plan="FREE",
            requests=0,
            limit=5
        )

        db.add(user)
        db.commit()

        return {
            "message": "Account created",
            "api_key": user.api_key
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        db.close()

# ======================
# LOGIN
# ======================
@app.post("/login")
def login(email: str, password: str):
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.email == email).first()

        if not user or user.password != password:
            return {"error": "Invalid credentials"}

        return {
            "api_key": user.api_key,
            "plan": user.plan,
            "requests": user.requests
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        db.close()

# ======================
# PREDICT (SAFE VERSION)
# ======================
@app.post("/predict")
def predict(
    V1: float, V2: float, V3: float,
    Amount: float, Time: float,
    api_key: str = Header(None)
):

    try:
        user = get_user(api_key)

        if not user:
            return {"error": "Invalid API key"}

        if user.requests >= user.limit:
            return {"error": "Limit reached"}

        X = np.array([[V1, V2, V3, Amount, Time]])
        X_scaled = scaler.transform(X)

        score = rf_model.predict_proba(X_scaled)[0][1]

        user.requests += 1

        db = SessionLocal()
        db.merge(user)
        db.commit()

        return {
            "fraud_score": float(score),
            "status": "FRAUD" if score > 0.5 else "NORMAL",
            "remaining": user.limit - user.requests
        }

    except Exception as e:
        return {"error": "Prediction failed", "details": str(e)}

# ======================
# STATS
# ======================
@app.get("/admin/stats")
def stats():
    db = SessionLocal()
    users = db.query(User).all()

    return {
        "total_users": len(users),
        "total_requests": sum(u.requests for u in users),
        "total_revenue": sum(u.revenue for u in users)
    }