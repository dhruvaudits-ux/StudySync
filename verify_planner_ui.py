from app import app, db
from models import User, StudyPlanner

def verify_planner_ui():
    with app.test_client() as client:
        with app.app_context():
            user = User.query.filter_by(email='student1@example.com').first()
            if not user:
                print("Error: Test user not found.")
                return

            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            # GET /planner to check subjects
            response = client.get('/planner')
            html = response.get_data(as_text=True)
            if "Physics" in html:
                print("Success: /planner template correctly renders subject dropdown.")
            else:
                print("Error: /planner template missing subjects.")

            # POST /planner/add
            print("\nSubmitting new task to /planner/add...")
            add_resp = client.post('/planner/add', data={
                'subject': 'Maths 2',
                'topic': 'Integration by parts',
                'priority': 'High',
                'notes': 'Practice 10 problems today.'
            }, follow_redirects=True)
            
            added_html = add_resp.get_data(as_text=True)
            if "Integration by parts" in added_html and "Maths 2" in added_html and "Practice 10 problems" in added_html:
                print("Success: New task submitted and rendered correctly on /planner!")
            else:
                print("Error: Task not properly rendered or added.")
                
            # Verify priority badge styling
            if "bg-red-50 text-red-600 border-red-200" in added_html:
                print("Success: 'High' priority badge styled correctly.")
            else:
                print("Error: Priority styling missing.")

            # Cleanup
            new_task = StudyPlanner.query.filter_by(topic="Integration by parts").first()
            if new_task:
                db.session.delete(new_task)
                db.session.commit()
                print("Success: Cleaned up test task.")

if __name__ == '__main__':
    verify_planner_ui()
