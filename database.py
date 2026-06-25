import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# -------------------------
# SAFE FALLBACK (IMPORTANT)
# -------------------------
if not DATABASE_URL:
    print("⚠️ WARNING: DATABASE_URL not set. Using SQLite fallback.")
    DATABASE_URL = "sqlite:///./local.db"

# -------------------------
# ENGINE
# -------------------------
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# -------------------------
# USER MODEL
# -------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    api_key = Column(String, unique=True)
    plan = Column(String, default="FREE")
    requests = Column(Integer, default=0)
    limit = Column(Integer, default=5)
    revenue = Column(Integer, default=0)

# -------------------------
# INIT DB
# -------------------------
def init_db():
    Base.metadata.create_all(bind=engine)