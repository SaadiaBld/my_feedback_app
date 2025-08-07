from dotenv import load_dotenv
from urllib.parse import quote_plus as urlquote
import os

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv('POSTGRES_USER')}:{urlquote(os.getenv('POSTGRES_PASSWORD'))}@localhost:5432/{os.getenv('POSTGRES_DB')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
