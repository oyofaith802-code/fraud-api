import uuid
import numpy as np
from fastapi import FastAPI, HTTPException, Header
from database import engine, SessionLocal, Base
from models import User
import joblib

app = FastAPI(title="Fraud SaaS V3")

Base.metadata.create_all(bind=engine)

rf_model = joblib.load("rf_model.pkl")
scaler = joblib.load("scaler.pkl")


@app.get("/")
def home():
    return {"status": "API Running", "version": "v3"}


# ---------------- DB FIX (IMPORTANT) ----------------
@app.get("/reset-db")
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return {"status": "db reset done"}


# ---------------- SIGNUP ----------------
@app.post("/signup")
def signup(email: str, password: str):

    db = SessionLocal()

    user = db.query(User).filter(User.email == email).first()
    if user:
        db.close()
        raise HTTPException(status_code=400, detail="User exists")

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
    db.close()

    return {"api_key": new_user.api_key}


# ---------------- LOGIN ----------------
@app.post("/login")
def login(email: str, password: str):

    db = SessionLocal()

    user = db.query(User).filter(User.email == email).first()

    if not user or user.password != password:
        db.close()
        raise HTTPException(status_code=401, detail="Invalid login")

    db.close()

    return {
        "api_key": user.api_key,
        "plan": user.plan,
        "requests": user.requests
    }


# ---------------- PREDICT ----------------
@app.post("/predict")
def predict(
    V1: float, V2: float, V3: float,
    Amount: float, Time: float,
    api_key: str = Header(None)
):

    db = SessionLocal()
    user = db.query(User).filter(User.api_key == api_key).first()

    if not user:
        db.close()
        raise HTTPException(status_code=401, detail="Invalid API key")

    if user.requests >= user.limit:
        db.close()
        return {"error": "Limit reached"}

    values = np.array([[V1, V2, V3, Amount, Time]])
    scaled = scaler.transform(values)

    score = rf_model.predict_proba(scaled)[0][1]

    user.requests += 1
    db.commit()
    db.close()

    return {
        "fraud_score": float(score),
        "status": "FRAUD" if score > 0.5 else "NORMAL",
        "remaining": user.limit - user.requests
    }


# ---------------- ADMIN ----------------
@app.get("/admin/stats")
def stats():

    db = SessionLocal()
    users = db.query(User).all()
    db.close()

    return {
        "total_users": len(users),
        "total_requests": sum(u.requests for u in users),
        "total_revenue": sum(u.revenue for u in users)
    }