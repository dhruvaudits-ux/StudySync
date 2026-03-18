from app import app, db
from models import StudyPlanner

with app.app_context():
    db.create_all()
    print("Database updated: StudyPlanner table created.")
