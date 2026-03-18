from app import app, db
from models import User, Subject

def verify_subject_model():
    with app.app_context():
        # 1. Create a subject for the test user
        user = User.query.filter_by(email='test@example.com').first()
        if user:
            new_subject = Subject(name='Engineering Mathematics', progress=25, owner=user)
            db.session.add(new_subject)
            db.session.commit()
            print(f"Success: Added subject '{new_subject.name}' to user '{user.name}'.")
            
            # 2. Verify relationship
            subjects = user.subjects
            print(f"Success: User subjects: {[s.name for s in subjects]}")
            
            # 3. Cleanup (optional, but good for idempotency if needed, here we'll keep it)
            # db.session.delete(new_subject)
            # db.session.commit()
        else:
            print("Error: Test user not found.")

if __name__ == '__main__':
    verify_subject_model()
