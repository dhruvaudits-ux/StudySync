from app import app, db
from models import PYQ

def verify_pyq_model():
    with app.app_context():
        # 1. Insert a test PYQ record
        test_pyq = PYQ(
            subject="Physics",
            year=2023,
            type="PYQ",
            file_name="physics_2023_pyq.pdf"
        )
        db.session.add(test_pyq)
        db.session.commit()
        print(f"Success: Inserted test PYQ for {test_pyq.subject} ({test_pyq.year}).")

        # 2. Query the database
        retrieved_pyq = PYQ.query.filter_by(subject="Physics", year=2023).first()
        if retrieved_pyq:
            print(f"Success: Retrieved PYQ from DB. File name is: {retrieved_pyq.file_name}")
            
            # 3. Clean up the test record
            db.session.delete(retrieved_pyq)
            db.session.commit()
            print("Success: Cleaned up test PYQ record.")
        else:
            print("Error: Could not retrieve the PYQ record.")

if __name__ == '__main__':
    verify_pyq_model()
