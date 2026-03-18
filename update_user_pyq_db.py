from app import app, db
from models import UserPYQ

with app.app_context():
    db.create_all()
    print("Database updated: UserPYQ table created.")
