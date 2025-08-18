import logging
import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import auth, dashboard

# Load environment variables
load_dotenv()

# --- Lignes de débogage à ajouter ---
print(f"DEBUG: os.getenv('ENV') = {os.getenv('ENV')}")
print(f"DEBUG: os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON') = { (os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')[:10] + '... (truncated)') if os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON') else 'None'}")
# --- Fin des lignes de débogage ---

# Config logging app
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("app")

def create_api_app():
    # Bloc 1: pour déploiement sur Render
    if os.getenv("ENV") == "prod":
        print("DEBUG: Bloc 'prod' des credentials activé.") # Ligne de débogage
        gcp_credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        if not gcp_credentials_json:
            raise RuntimeError("La variable GOOGLE_APPLICATION_CREDENTIALS_JSON n'est pas définie")

        # Écrit le fichier temporaire à partir du contenu JSON
        creds_path = "/tmp/gcp_creds.json"
        with open(creds_path, "w") as f:
            f.write(gcp_credentials_json)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
        print(f"DEBUG: GOOGLE_APPLICATION_CREDENTIALS set to {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}") # Ligne de débogage
    else:
        print("DEBUG: Bloc 'prod' des credentials SKIPPÉ. ENV n'est pas 'prod'.") # Ligne de débogage

    app = FastAPI(
        title="Dashboard API",
        description="API d'accès aux KPIs hebdomadaires",
        version="1.0.0"
    )

    # Logs des routes au démarrage
    @app.on_event("startup")
    async def log_routes():
        for r in app.routes:
            try:
                logger.info("ROUTE %s %s", getattr(r, "methods", None), r.path)
            except Exception:
                pass

    # Middleware: log minimal des requêtes
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info("REQ %s %s", request.method, request.url.path)
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("Unhandled exception")
            raise
        logger.info("RES %s %s -> %s", request.method, request.url.path, response.status_code)
        return response

    # Handler global: JSON 500 propre
    @app.exception_handler(Exception)
    async def all_errors(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse({"ok": False, "error": "internal_error"}, status_code=500)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(dashboard.router, prefix="/api/dashboard")
    app.include_router(auth.router, tags=["Authentication"])
    return app

app = create_api_app()