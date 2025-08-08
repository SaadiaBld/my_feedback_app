from dotenv import load_dotenv
from urllib.parse import quote_plus as urlquote
import os

load_dotenv()

class Config:
    
    ENV = os.getenv("ENV", "dev").lower()
    SECRET_KEY = os.getenv("SECRET_KEY", "secret_key")

    if ENV == "prod":
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL doit être défini en environnement 'prod'.")
    else:
        # En dev ou test, on reconstruit l’URL à partir des variables POSTGRES_*
        POSTGRES_USER = os.getenv("POSTGRES_USER")
        POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
        POSTGRES_DB = os.getenv("POSTGRES_DB")
        POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
        POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

        if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
            raise ValueError("Variables POSTGRES_* manquantes en environnement dev/test.")

        DATABASE_URL = (
            f"postgresql://{POSTGRES_USER}:{urlquote(POSTGRES_PASSWORD)}"
            f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    print(f"[Config] ENV: {ENV}")
    print(f"[Config] SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}")


# class Config:
#     ENV = os.getenv("ENV", "dev")
#     SECRET_KEY = os.getenv("SECRET_KEY", "secret_key")

#     # 1. Priorité à DATABASE_URL (comme sur Render)
#     DATABASE_URL = os.getenv("DATABASE_URL")

#     # 2. Sinon on reconstruit l'URL à partir des variables classiques (pour le local)
#     if not DATABASE_URL:
#         POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
#         POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
#         POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
#         POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
#         POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

#         if ENV != "test":
#             if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
#                 raise ValueError("Variables POSTGRES_* manquantes pour construire l'URL PostgreSQL.")

#         DATABASE_URL = (
#             f"postgresql://{POSTGRES_USER}:{urlquote(POSTGRES_PASSWORD)}"
#             f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
#         )

#     SQLALCHEMY_DATABASE_URI = DATABASE_URL
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

#     print(f"[Config] ENV: {ENV}")
#     print(f"[Config] SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}")
