# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from passlib.hash import bcrypt
from app import db
from app.models import User

auth_bp = Blueprint("auth", __name__)

def verify_password(plain: str, stored_hash: str) -> bool:
    """Gère pbkdf2 (Werkzeug) et bcrypt (passlib)."""
    if not stored_hash:
        return False
    if stored_hash.startswith("pbkdf2:"):
        return check_password_hash(stored_hash, plain)
    if stored_hash.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            return bcrypt.verify(plain, stored_hash)
        except Exception:
            return False
    # fallback: tente Werkzeug
    try:
        return check_password_hash(stored_hash, plain)
    except Exception:
        return False

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        remember = bool(request.form.get("remember"))

        print(f"[LOGIN] Tentative pour {email}")

        user = User.query.filter_by(email=email).first()
        if user:
            print(f"[LOGIN] Utilisateur trouvé : {user.email}")
            print(f"[LOGIN] Hash stocké : {user.password_hash[:25]}...")
        else:
            print(f"[LOGIN] Aucun utilisateur trouvé pour cet email")

        ok = user and verify_password(password, user.password_hash)
        print(f"[LOGIN] Résultat vérification mot de passe : {ok}")

        if ok:
            login_user(user, remember=remember)
            return redirect(url_for("dashboard.dashboard"))

        flash("Email ou mot de passe incorrect", "error")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

