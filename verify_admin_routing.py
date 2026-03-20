import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from app import app, db
from models import User
from werkzeug.security import generate_password_hash
from datetime import datetime

def test_admin_routing():
    with app.test_client() as client:
        # 0. Setup test users FIRST
        print("Setup: Creating test users...")
        with app.app_context():
            # Clean up if exists
            User.query.filter_by(email="test_student@test.com").delete()
            User.query.filter_by(email="test_admin@test.com").delete()
            
            student = User(name="Test Student", email="test_student@test.com", password=generate_password_hash("pass"), role="student")
            admin = User(name="Test Admin", email="test_admin@test.com", password=generate_password_hash("pass"), role="admin")
            db.session.add(student)
            db.session.add(admin)
            db.session.commit()

        # 1. Test unauthenticated access
        print("\nTest 1: Unauthenticated access to /admin/dashboard")
        response = client.get('/admin/dashboard', follow_redirects=True)
        # Should redirect to login
        if b"Login" in response.data or b"Please login" in response.data:
            print("[OK] Unauthenticated user redirected to login.")
        else:
            print("[FAIL] Unauthenticated user not redirected correctly.")

        # 2. Test /admin redirect WHILE LOGGED IN
        print("\nTest 2: /admin redirect for authenticated Admin")
        client.post('/login', data={'email': 'test_admin@test.com', 'password': 'pass'}, follow_redirects=True)
        response = client.get('/admin', follow_redirects=True)
        if b"Admin Portal" in response.data or b"System Overview" in response.data:
            print("[OK] /admin correctly leads to admin portal.")
        else:
            print("[FAIL] /admin did not lead to admin portal.")

        # 3. Test student access to admin route
        print("\nTest 3: Student access to /admin/dashboard")
        client.get('/logout')
        client.post('/login', data={'email': 'test_student@test.com', 'password': 'pass'}, follow_redirects=True)
        response = client.get('/admin/dashboard', follow_redirects=True)
        if response.status_code == 403:
            print("[OK] Student access to /admin/dashboard forbidden (403).")
        else:
            print(f"[FAIL] Student access to /admin/dashboard status code: {response.status_code}")

        # Cleanup
        with app.app_context():
            User.query.filter_by(email="test_student@test.com").delete()
            User.query.filter_by(email="test_admin@test.com").delete()
            db.session.commit()

if __name__ == "__main__":
    test_admin_routing()
