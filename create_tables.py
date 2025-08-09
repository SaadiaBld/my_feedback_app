from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    user = User.query.first()
    print(user.id, user.email)
