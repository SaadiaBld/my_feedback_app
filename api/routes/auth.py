# 
# api/auth.py
import os
import sys
import traceback
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from api.security import create_access_token, get_current_user 

router = APIRouter(tags=["Authentication"])

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL") or os.getenv("AUTH_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

@router.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends()):
    print("--- Entering /token endpoint ---", file=sys.stderr)
    print(f"ADMIN_EMAIL from env: {ADMIN_EMAIL}", file=sys.stderr)
    print(f"form.username: {form.username}", file=sys.stderr)

    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        print("ERROR: ADMIN_EMAIL or ADMIN_PASSWORD not configured.", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Auth not configured (ADMIN_EMAIL/ADMIN_PASSWORD missing)")

    if not (form.username == ADMIN_EMAIL and form.password == ADMIN_PASSWORD):
        print("ERROR: Invalid credentials.", file=sys.stderr)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    print("Credentials verified. Creating access token...", file=sys.stderr)
    try:
        token = create_access_token({"sub": ADMIN_EMAIL}, expires_delta=timedelta(hours=1))
        print("Access token created successfully.", file=sys.stderr)
    except Exception as e:
        print(f"ERROR during create_access_token: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise
        
    return {"access_token": token, "token_type": "bearer"}

@router.get("/auth/check")
def auth_check(email: str = Depends(get_current_user)):
    return {"ok": True, "sub": email}