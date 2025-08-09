from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    migrate.init_app(app, db)

    from app import models

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix="/")

    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))  

    return app
