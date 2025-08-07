from dotenv import load_dotenv
from urllib.parse import quote_plus as urlquote
import os

load_dotenv()

class Config:
    ENV = os.getenv("ENV", "dev")

    if ENV == "test":
        SQLALCHEMY_DATABASE_URI = ("postgresql://postgres:postgres@localhost:5432/test_db")
    else:
        # Database configuration
        POSTGRES_USER = os.getenv('POSTGRES_USER')
        POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
        POSTGRES_DB = os.getenv('POSTGRES_DB')
        POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
        POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
        
        if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
            raise ValueError("Les variables d'environnement de la base de données (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB) ne sont pas toutes définies.")

        SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{urlquote(POSTGRES_PASSWORD)}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
