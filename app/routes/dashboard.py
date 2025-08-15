from flask import Blueprint, render_template, current_app, session
from flask_login import login_required
import os

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    api_base_url = os.getenv('API_BASE_URL', 'http://127.0.0.1:10000')
    jwt_token = session.get("jwt_token") # Récupérer le token de la session
    return render_template("dashboard.html", api_base_url=api_base_url, is_testing=current_app.config["TESTING"], jwt_token=jwt_token)