import os
import json
import base64
from google.cloud import bigquery
from google.oauth2.service_account import Credentials
from .database import SessionLocal

def get_bq_client():
    # Recommended: Use base64-encoded credentials to avoid newline issues in production
    if "GCP_SA_JSON_B64" in os.environ:
        info = json.loads(base64.b64decode(os.environ["GCP_SA_JSON_B64"]).decode("utf-8"))
        creds = Credentials.from_service_account_info(info)
        return bigquery.Client(credentials=creds, project=info["project_id"])
    
    # Fallback to Application Default Credentials (for local dev or old setup)
    # This will use GOOGLE_APPLICATION_CREDENTIALS if set by the logic in main.py
    return bigquery.Client()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()