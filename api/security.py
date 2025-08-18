# api/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os, sys, traceback

load_dotenv()

ENV = os.getenv("ENV", "prod")
SECRET_KEY = "test-secret-key" if ENV == "test" else os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

try:
    JWT_LEEWAY_SECONDS = int(os.getenv("JWT_LEEWAY_SECONDS", "60"))
except ValueError:
    JWT_LEEWAY_SECONDS = 60

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set. Define it in Render's environment variables or .env for local.")

# Important: chemin exact de la route token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode = {**data, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={
                "require_exp": True,
                "leeway": JWT_LEEWAY_SECONDS,
            },
        )
        email: Optional[str] = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: 'sub' claim missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return email
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token)
