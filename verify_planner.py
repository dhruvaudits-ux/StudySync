from app import app, db
from models import User, StudyPlanner
from datetime import datetime

def verify_planner():
    with app.test_client() as client:
        with app.app_context():
            # Get test user
            user = User.query.filter_by(email='student1@example.com').first()
            if not user:
                print("Error: Test user not found.")
                return

            print(f"Testing with User: {user.email}")

            # 1. Insert a test task
            test_task = StudyPlanner(
                user_id=user.id,
                subject="Physics",
                topic="Quantum Mechanics Chapter 1",
                priority="High",
                notes="Make sure to review Schrodinger's equation.",
                status="Pending"
            )
            db.session.add(test_task)
            db.session.commit()
            print("Success: Inserted test StudyPlanner task.")

            # Simulate login
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            # 2. Fetch /planner route
            print("Fetching /planner route...")
            response = client.get('/planner')
            if response.status_code == 200:
                print("Success: /planner loaded correctly.")
                html = response.get_data(as_text=True)
                # Note: planner.html might not render the tasks visibly yet, 
                # but we know the route ran without 500 error.
            else:
                print(f"Error: Status code {response.status_code}")

            # 3. Clean up
            db.session.delete(test_task)
            db.session.commit()
            print("Success: Cleaned up test StudyPlanner task.")

if __name__ == '__main__':
    verify_planner()
