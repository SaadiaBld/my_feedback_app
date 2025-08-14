# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from app import db
from app.models import User
from jose import jwt
from datetime import datetime, timedelta
import os

auth_bp = Blueprint("auth", __name__)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30) # Durée par défaut pour le token Flask
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain: str, stored_hash: str) -> bool:
    """Vérifie le mot de passe en utilisant Werkzeug."""

    if not stored_hash:
        return False
    # Tente la vérification avec Werkzeug, qui gère pbkdf2 et d'autres formats.
    try:
        return check_password_hash(stored_hash, plain)
    except Exception:
        return False

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = (request.form.get("password") or "").strip()
        remember = bool(request.form.get("remember"))

        # Logs sur le mot de passe entré
        current_app.logger.info(f"[LOGIN] Tentative pour '{email}'")
        current_app.logger.info(f"[LOGIN] Longueur mot de passe saisi: {len(password)}")
        current_app.logger.info(f"[LOGIN] Mot de passe saisi (debug): '{password}'")

        user = User.query.filter_by(email=email).first()

        if user:
            # Logs sur le mot de passe stocké
            current_app.logger.info(f"[LOGIN] Utilisateur trouvé: {user.email}")
            current_app.logger.info(f"[LOGIN] Longueur hash stocké: {len(user.password_hash)}")
            current_app.logger.info(f"[LOGIN] Début hash stocké: {user.password_hash[:30]}...")

            password_ok = verify_password(password, user.password_hash)
            current_app.logger.info(f"[LOGIN] Résultat vérification mot de passe: {password_ok}")

            if password_ok:
                login_user(user, remember=remember)
                # Générer le token JWT et le stocker dans la session
                access_token = create_access_token(data={"sub": user.email})
                session["jwt_token"] = access_token
                return redirect(url_for("dashboard.dashboard"))
        else:
            current_app.logger.info(f"[LOGIN] Aucun utilisateur trouvé pour '{email}'")

        flash("Email ou mot de passe incorrect", "error")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop("jwt_token", None) # Supprimer le token de la session lors de la déconnexion
    return redirect(url_for("auth.login"))

