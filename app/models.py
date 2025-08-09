from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'app_user'  # Flask-SQLAlchemy va gérer les guillemets
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

def __repr__(self):
    return f"<User id={self.id} email={self.email}>"
