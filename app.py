import uuid
import numpy as np
import joblib
from fastapi import FastAPI, Header, HTTPException
from db import SessionLocal, User, RequestLog, Base, engine
from auth import create_token, verify_token
import time
import requests

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SaaS v3 Production")

model = joblib.load("models.pkl")
scaler = joblib.load("scaler.pkl")


# ======================
# SIGNUP
# ======================
@app.post("/signup")
def signup(email: str, password: str):
    db = SessionLocal()

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


# ======================
# LOGIN (JWT)
# ======================
@app.post("/login")
def login(email: str, password: str):
    db = SessionLocal()

    user = db.query(User).filter(
        User.email == email,
        User.password == password
    ).first()

    if not user:
        raise HTTPException(401, "invalid")

    token = create_token(user.id)

    return {"token": token}


# ======================
# RATE LIMIT
# ======================
def check_limit(user: User):
    if user.requests >= user.limit:
        raise HTTPException(429, "Upgrade required")


# ======================
# PREDICT API
# ======================
@app.post("/predict")
def predict(
    V1: float, V2: float, V3: float,
    Amount: float, Time: float,
    authorization: str = Header(None)
):

    data = verify_token(authorization)
    if not data:
        raise HTTPException(401, "Invalid token")

    db = SessionLocal()
    user = db.query(User).filter(User.id == data["user_id"]).first()

    check_limit(user)

    start = time.time()

    X = np.array([[V1, V2, V3, Amount, Time]])
    X = scaler.transform(X)

    score = model.predict_proba(X)[0][1]

    user.requests += 1

    latency = time.time() - start

    db.add(RequestLog(
        user_id=user.id,
        endpoint="/predict",
        latency=latency
    ))

    db.commit()

    return {
        "fraud_score": float(score),
        "status": "FRAUD" if score > 0.5 else "NORMAL",
        "remaining": user.limit - user.requests
    }