from app import app, db
from models import User, Subject

def verify_progress_update():
    with app.test_client() as client:
        with app.app_context():
            user = User.query.filter_by(email='student1@example.com').first()
            if not user:
                print("Error: User 'student1@example.com' not found.")
                return
            
            subject = Subject.query.filter_by(user_id=user.id).first()
            if not subject:
                print("Error: No subjects found for the user.")
                return
                
            original_progress = subject.progress
            print(f"Testing Subject: {subject.name} (ID: {subject.id})")
            print(f"Original Progress: {original_progress}%")
            
            # Create a test session to simulate login
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            # Attempt to update progress to 88%
            new_val = 88
            print(f"\nSending POST request to /update_progress/{subject.id} with progress={new_val}...")
            response = client.post(f'/update_progress/{subject.id}', data={'progress': str(new_val)}, follow_redirects=True)
            
            # Verify DB was actually updated
            updated_subject = Subject.query.get(subject.id)
            print(f"Resulting Progress in DB: {updated_subject.progress}%")
            
            if updated_subject.progress == new_val:
                print("\nSuccess! Progress successfully updated in the database.")
            else:
                print("\nFailure! Progress was not updated.")
                
            # Attempt to set invalid progress
            print(f"\nSending POST request to /update_progress/{subject.id} with invalid progress=150...")
            response = client.post(f'/update_progress/{subject.id}', data={'progress': '150'}, follow_redirects=True)
            
            final_subject = Subject.query.get(subject.id)
            print(f"Resulting Progress in DB: {final_subject.progress}%")
            if final_subject.progress == new_val:
                print("Success! Invalid progress was rejected.")
            else:
                print("Failure! Invalid progress was accepted.")

if __name__ == '__main__':
    verify_progress_update()
