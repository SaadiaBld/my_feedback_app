from fastapi import FastAPI
from .routes import dashboard
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()  # Charge automatiquement les variables du fichier .env

def create_api_app():
    # Bloc 1: pour déploiement sur Render
    if os.getenv("ENV") == "prod":
        gcp_credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        if not gcp_credentials_json:
            raise RuntimeError("La variable GOOGLE_APPLICATION_CREDENTIALS_JSON n'est pas définie")

        # Écrit le fichier temporaire à partir du contenu JSON
        creds_path = "/tmp/gcp_creds.json"
        with open(creds_path, "w") as f:
            f.write(gcp_credentials_json)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path

    # Bloc local (à activer pour exécution locale)
    # gcp_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    # if os.getenv("ENV") != "test":
    #     if not gcp_creds or not os.path.exists(gcp_creds):
    #         raise FileNotFoundError(f"Fichier de credentials introuvable : {gcp_creds}")

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


app = create_api_app()
