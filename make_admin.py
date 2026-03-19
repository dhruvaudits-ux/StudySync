"""
make_admin.py — Promote a user to admin role.

Usage:
    python make_admin.py <email>

Example:
    python make_admin.py yourname@example.com
"""
import sys
from app import app, db
from models import User

def make_admin(email: str):
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"[ERROR] No user found with email: {email}")
            sys.exit(1)
        user.role = 'admin'
        db.session.commit()
        print(f"[OK] '{user.name}' ({user.email}) is now an admin.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py <email>")
        sys.exit(1)
    make_admin(sys.argv[1])
