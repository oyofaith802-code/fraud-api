from sqlalchemy import Column, String, Integer, Float
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    api_key = Column(String, unique=True, index=True)

    plan = Column(String, default="FREE")
    requests = Column(Integer, default=0)
    limit = Column(Integer, default=5)

    revenue = Column(Float, default=0.0)