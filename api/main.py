from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from api.routes import dashboard, auth
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import traceback, sys

load_dotenv()

# --- Lignes de débogage à ajouter ---
print(f"DEBUG: os.getenv('ENV') = {os.getenv('ENV')}")
print(f"DEBUG: os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON') = { (os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')[:10] + '... (truncated)') if os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON') else 'None'}")
# --- Fin des lignes de débogage ---

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

    @app.exception_handler(Exception)
    async def all_errors(request: Request, exc: Exception):
        traceback.print_exc(file=sys.stderr)  # visible dans les logs Render
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
