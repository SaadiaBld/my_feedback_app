from dotenv import load_dotenv
from urllib.parse import quote_plus as urlquote
import os

load_dotenv()

class Config:
    ENV = os.getenv("ENV", "dev")
    SECRET_KEY = os.getenv("SECRET_KEY", "secret_key")
    # Valeurs par défaut pour tous les environnements
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

    if ENV != "test":
        # On exige que les variables soient bien définies (sauf en test)
        if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
            raise ValueError("Les variables d'environnement de la base de données (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB) ne sont pas toutes définies.")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGRES_USER}:{urlquote(POSTGRES_PASSWORD)}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    print(f"Configuration loaded: {ENV}")
    print(f"Database URI: {SQLALCHEMY_DATABASE_URI}")
    print(f"Secret Key: {SECRET_KEY}")