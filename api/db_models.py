from sqlalchemy import Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "app_user" # Doit correspondre au nom de table de Flask-SQLAlchemy

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
