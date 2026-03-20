import os
from app import app, db, User
from sqlalchemy import text

def migrate():
    with app.app_context():
        # 1. Ensure upload directory exists
        upload_dir = os.path.join('static', 'uploads')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            print(f"Created directory: {upload_dir}")
        else:
            print(f"Directory already exists: {upload_dir}")

        # 2. Update existing users
        # Users might have paths like 'uploads/profile_pics/...' from the old system
        # or NULL. We want to reset them to 'default.png' for this migration
        # or just the filename if it was already updated.
        
        users = User.query.all()
        updated_count = 0
        for user in users:
            if not user.profile_pic or 'uploads/profile_pics/' in user.profile_pic:
                user.profile_pic = 'default.png'
                updated_count += 1
        
        db.session.commit()
        print(f"Updated {updated_count} users to use 'default.png'.")
        
        # 3. Handle default.png placeholder if it doesn't exist
        default_pic_path = os.path.join(upload_dir, 'default.png')
        if not os.path.exists(default_pic_path):
            print(f"WARNING: {default_pic_path} does not exist. Please add a default avatar image.")
            # We could potentially create a placeholder here if PIL was guaranteed
        else:
            print(f"Found default.png at {default_pic_path}")

if __name__ == '__main__':
    migrate()
