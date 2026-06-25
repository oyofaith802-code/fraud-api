from sqlalchemy import create_engine, Column, String, Integer, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True)
    api_key = Column(String, unique=True)
    plan = Column(String)
    requests = Column(Integer, default=0)
    limit = Column(Integer, default=5)
    revenue = Column(Float, default=0)


def init_db():
    Base.metadata.create_all(engine)