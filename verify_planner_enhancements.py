from app import app, db
from models import User, StudyPlanner, PYQ

def verify_planner_enhancements():
    with app.test_client() as client:
        with app.app_context():
            user = User.query.filter_by(email='student1@example.com').first()
            if not user:
                print("Error: Test user not found.")
                return

            # Simulate login
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            # 1. Test toggling the task
            task = StudyPlanner(
                user_id=user.id,
                subject="Physics",
                topic="Quantum Mechanics Chapter 1",
                priority="High",
                status="Pending"
            )
            db.session.add(task)
            db.session.commit()
            
            original_status = task.status
            print(f"Original status for task '{task.topic}': {original_status}")
            
            print(f"Toggling task {task.id}...")
            client.post(f'/planner/toggle/{task.id}')
            db.session.refresh(task)
            
            print(f"New status: {task.status}")
            if task.status != original_status:
                print("Success: Task successfully toggled!")
            else:
                print("Error: Task toggle failed.")

            # 2. Test auto-generating task from PYQ interaction
            pyq = PYQ.query.first()
            if not pyq:
                print("Error: No PYQ found.")
                return
                
            print(f"\nMarking PYQ {pyq.id} ({pyq.subject}) as 'important'...")
            client.post(f'/pyq/{pyq.id}/interaction', data={'status': 'important'})
            
            # Check if a task was Auto-generated
            generated_task = StudyPlanner.query.filter_by(user_id=user.id, priority='High').filter(StudyPlanner.topic.contains('Revise')).first()
            if generated_task:
                print(f"Success: Auto-generated task found: '{generated_task.topic}'!")
                # Cleanup
                db.session.delete(generated_task)
                db.session.commit()
                print("Success: Cleaned up generated task.")
            else:
                print("Error: Auto-generated task not found in DB.")
                
            db.session.delete(task)
            db.session.commit()

if __name__ == '__main__':
    verify_planner_enhancements()
