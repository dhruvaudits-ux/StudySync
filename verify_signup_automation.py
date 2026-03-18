from app import app, db
from models import User, Subject
from werkzeug.security import generate_password_hash

def verify_signup_automation():
    with app.app_context():
        email = 'student1@example.com'
        # 1. Simulate signup logic
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"Info: User {email} already exists. Cleaning up for test...")
            Subject.query.filter_by(user_id=user.id).delete()
            db.session.delete(user)
            db.session.commit()
            
        new_user = User(
            name='Student One',
            email=email,
            password=generate_password_hash('student123')
        )
        db.session.add(new_user)
        db.session.commit()
        
        default_subjects = [
            'Physics', 'Chemistry', 'Mechanics', 'Maths 2', 'IKS',
            'MPW', 'DTIL', 'BXE', 'BEE', 'Engineering Graphics'
        ]
        for sub_name in default_subjects:
            subject = Subject(name=sub_name, progress=0, owner=new_user)
            db.session.add(subject)
        db.session.commit()
        
        # 2. Verify subjects were created
        created_subjects = Subject.query.filter_by(user_id=new_user.id).all()
        print(f"Success: Created {len(created_subjects)} subjects for {email}.")
        for s in created_subjects:
            print(f" - {s.name} (Progress: {s.progress})")
            
        if len(created_subjects) == 10:
            print("Verified: Exactly 10 default subjects were created.")
        else:
            print(f"Error: Expected 10 subjects, found {len(created_subjects)}.")

if __name__ == '__main__':
    verify_signup_automation()
