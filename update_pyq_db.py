from app import app, db
from models import PYQ

with app.app_context():
    db.create_all()
    print("Database updated: PYQ table created.")
