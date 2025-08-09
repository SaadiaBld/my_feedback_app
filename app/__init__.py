from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from .config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Importer les modèles pour Alembic
    from . import models

    # Blueprints
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from .routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)  # pas besoin de prefix "/", il gère /dashboard

    # Healthcheck
    @app.get("/healthz")
    def healthz():
        return "ok", 200

    # Page d'accueil
    @app.get("/")
    def index():
        return "Hello from Render 🎉", 200

    return app
