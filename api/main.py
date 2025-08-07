from fastapi import FastAPI
from api.routes import dashboard
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()  # Charge automatiquement les variables du fichier .env

def create_api_app():
    # Vérifier le fichier credentials uniquement hors test
    gcp_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if os.getenv("ENV") != "test":
        if not gcp_creds or not os.path.exists(gcp_creds):
            raise FileNotFoundError(f"Fichier de credentials introuvable : {gcp_creds}")

    app = FastAPI(
        title="Dashboard API",
        description="API d'accès aux KPIs hebdomadaires",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(dashboard.router, prefix="/api/dashboard")

    return app

#app.include_router(health.router)
