import os
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL missing in environment variables")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)

    api_key = Column(String, unique=True)

    verification_code = Column(Integer, default=0)
    verified = Column(Integer, default=0)

    plan = Column(String, default="FREE")

    requests = Column(Integer, default=0)
    limit = Column(Integer, default=2)

    revenue = Column(Float, default=0)


def init_db():
    Base.metadata.create_all(bind=engine)