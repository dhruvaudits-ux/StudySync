from app import app, db
from models import User, StudyPlanner, PYQ, Activity

def verify_activity_tracking():
    with app.test_client() as client:
        with app.app_context():
            user = User.query.filter_by(email='student1@example.com').first()
            if not user:
                print("Error: Test user not found.")
                return
                
            # Clear old activities for a clean test
            Activity.query.filter_by(user_id=user.id).delete()
            db.session.commit()

            # 1. Simulate login (the client POSTs to /login)
            print("Logging in via client to trigger 'login' activity...")
            client.post('/login', data={'email': 'student1@example.com', 'password': 'password123'})
            
            # 2. Add task
            print("Adding task via client to trigger 'added_task'...")
            client.post('/planner/add', data={'subject': 'Physics', 'topic': 'Telemetry Test', 'priority': 'Medium'})
            
            # 3. Complete task
            task = StudyPlanner.query.filter_by(topic='Telemetry Test').first()
            if task:
                print(f"Toggling task {task.id} via client to trigger 'completed_task'...")
                client.post(f'/planner/toggle/{task.id}')
            
            # 4. Interactive PYQ
            pyq = PYQ.query.first()
            if pyq:
                print(f"Marking PYQ {pyq.id} completed via client to trigger 'completed_pyq'...")
                client.post(f'/pyq/{pyq.id}/interaction', data={'status': 'completed'})

            # 5. Check the DB directly
            activities = Activity.query.filter_by(user_id=user.id).all()
            actions_found = [a.action for a in activities]
            print("\nActivities found in DB:", actions_found)
            
            for required in ['login', 'added_task', 'completed_task', 'completed_pyq']:
                if required in actions_found:
                    print(f"Success: '{required}' tracked.")
                else:
                    print(f"Error: '{required}' missing.")
                    
            # 6. Hit the /activity endpoint
            print("\nFetching /activity endpoint...")
            response = client.get('/activity')
            if response.status_code == 200:
                print("Success: /activity loaded correctly.")
            else:
                print(f"Error: Status {response.status_code}")

            # Cleanup
            Activity.query.filter_by(user_id=user.id).delete()
            if task:
                db.session.delete(task)
            db.session.commit()
            print("Success: Cleaned up tests.")

if __name__ == '__main__':
    verify_activity_tracking()
