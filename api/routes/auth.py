from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from ..db_models import User
from .deps import get_db
from werkzeug.security import check_password_hash
from ..security import create_access_token
from datetime import timedelta

router = APIRouter()

@router.post("/token", summary="Crée un jeton d'accès JWT")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    """
    Fournissez un email (dans le champ username) et un mot de passe pour obtenir un jeton d'accès.
    """
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not check_password_hash(user.password_hash, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
