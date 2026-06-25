import uuid
import numpy as np
from fastapi import FastAPI, HTTPException, Header
from database import engine, SessionLocal, Base
from models import User
import joblib

# =========================
# APP INIT
# =========================
app = FastAPI(title="Fraud SaaS V3 Clean")

# =========================
# CREATE TABLES
# =========================
Base.metadata.create_all(bind=engine)

# =========================
# LOAD ML MODEL
# =========================
rf_model = joblib.load("rf_model.pkl")
scaler = joblib.load("scaler.pkl")

# =========================
# HOME
# =========================
@app.get("/")
def home():
    return {"status": "Fraud SaaS Running", "version": "v3"}

# =========================
# DB SESSION
# =========================
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass

def get_user(api_key: str):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.api_key == api_key).first()
    finally:
        db.close()

# =========================
# SIGNUP
# =========================
@app.post("/signup")
def signup(email: str, password: str):

    db = SessionLocal()

    try:
        user = db.query(User).filter(User.email == email).first()

        if user:
            raise HTTPException(status_code=400, detail="User already exists")

        new_user = User(
            id=str(uuid.uuid4()),
            email=email,
            password=password,
            api_key="fk_" + uuid.uuid4().hex[:24],
            plan="FREE",
            requests=0,
            limit=5,
            revenue=0.0
        )

        db.add(new_user)
        db.commit()

        return {
            "message": "Account created",
            "api_key": new_user.api_key
        }

    finally:
        db.close()

# =========================
# LOGIN
# =========================
@app.post("/login")
def login(email: str, password: str):

    db = SessionLocal()

    try:
        user = db.query(User).filter(User.email == email).first()

        if not user or user.password != password:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return {
            "api_key": user.api_key,
            "plan": user.plan,
            "requests": user.requests
        }

    finally:
        db.close()

# =========================
# PREDICT
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
        return {"error": "Limit reached. Upgrade required."}

    values = np.array([[V1, V2, V3, Amount, Time]])
    scaled = scaler.transform(values)

    score = rf_model.predict_proba(scaled)[0][1]

    user.requests += 1

    db = SessionLocal()
    try:
        db.merge(user)
        db.commit()
    finally:
        db.close()

    return {
        "fraud_score": float(score),
        "status": "FRAUD" if score > 0.5 else "NORMAL",
        "remaining": user.limit - user.requests
    }

# =========================
# ADMIN STATS
# =========================
@app.get("/admin/stats")
def stats():

    db = SessionLocal()

    try:
        users = db.query(User).all()

        return {
            "total_users": len(users),
            "total_requests": sum(u.requests for u in users),
            "total_revenue": sum(u.revenue for u in users)
        }

    finally:
        db.close()