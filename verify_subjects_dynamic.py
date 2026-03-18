from app import app, db
from models import User, Subject

def verify_subjects_dynamic():
    with app.app_context():
        # Check for multiple users
        users = User.query.all()
        for user in users:
            subjects = Subject.query.filter_by(user_id=user.id).all()
            print(f"User: {user.email} | Subjects found: {len(subjects)}")
            for s in subjects:
                print(f"  - {s.name}")
            print("-" * 20)

if __name__ == '__main__':
    verify_subjects_dynamic()
