from app import app, db
from models import Subject

with app.app_context():
    db.create_all()
    print("Database updated: Subject table created.")
