import os
import json
import base64
from google.cloud import bigquery
from google.oauth2.service_account import Credentials
from .database import SessionLocal

def get_bq_client():
    info = json.loads(base64.b64decode(os.environ["GCP_SA_JSON_B64"]).decode("utf-8"))
    creds = Credentials.from_service_account_info(info)
    return bigquery.Client(credentials=creds, project=info["project_id"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
