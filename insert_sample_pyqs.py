from app import app, db
from models import PYQ
import os

def insert_sample_pyqs():
    with app.app_context():
        # Insert sample PYQ
        file_name = "physics_2022.pdf"
        
        # Check if the file physically exists just to be safe
        pdf_path = os.path.join(app.root_path, 'static', 'pdfs', file_name)
        if not os.path.exists(pdf_path):
            print(f"Warning: {file_name} not found in static/pdfs folder, but inserting record anyway.")
            
        existing = PYQ.query.filter_by(file_name=file_name).first()
        if not existing:
            new_pyq = PYQ(
                subject="Physics",
                year=2022,
                type="PYQ",
                file_name=file_name
            )
            db.session.add(new_pyq)
            db.session.commit()
            print(f"Inserted: {new_pyq.subject}, {new_pyq.year}, {new_pyq.type}, {new_pyq.file_name}")
        else:
            print(f"Record for {file_name} already exists.")

if __name__ == '__main__':
    insert_sample_pyqs()
