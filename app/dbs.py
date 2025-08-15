import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import Config # On réutilise la config pour l'URL

# Moteur de base de données SQLAlchemy standard
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

# Créateur de session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dépendance FastAPI pour fournir une session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()