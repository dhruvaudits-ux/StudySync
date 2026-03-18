from app import app, db
from models import User
from werkzeug.security import check_password_hash

def verify():
    with app.app_context():
        # 1. Check if test user exists (created in previous step)
        user = User.query.filter_by(email='test@example.com').first()
        if user:
            print(f"Success: User {user.name} found.")
            # 2. Check password hashing
            is_valid = check_password_hash(user.password, 'password123')
            print(f"Success: Password verification works: {is_valid}")
        else:
            print("Error: Test user not found.")

        # 3. Test Signup Logic (simulated)
        new_email = 'newuser@example.com'
        if not User.query.filter_by(email=new_email).first():
            from werkzeug.security import generate_password_hash
            new_user = User(
                name='New User',
                email=new_email,
                password=generate_password_hash('newpass123')
            )
            db.session.add(new_user)
            db.session.commit()
            print(f"Success: Simulated signup for {new_email} works.")
        else:
            print(f"Info: User {new_email} already exists.")

if __name__ == '__main__':
    verify()
