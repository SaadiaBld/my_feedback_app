from dotenv import load_dotenv
from urllib.parse import quote_plus as urlquote
import os

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")

    # Database configuration
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_DB = os.getenv('POSTGRES_DB')

    if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
        raise ValueError("Les variables d'environnement de la base de données (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB) ne sont pas toutes définies.")

    SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{urlquote(POSTGRES_PASSWORD)}@localhost:5432/{POSTGRES_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
