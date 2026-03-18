from app import app, db
from models import Activity

with app.app_context():
    db.create_all()
    print("Database updated: Activity table created.")
