from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from app import db, login_manager
from app.models import User

auth_bp = Blueprint("auth", __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()
        print("*****Hash stocké :", user.password_hash)

        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            return redirect(url_for("dashboard.dashboard"))
        flash("Email ou mot de passe incorrect", "error")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
