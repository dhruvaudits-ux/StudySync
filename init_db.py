from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='test@example.com').first():
        user = User(
            name='Test User',
            email='test@example.com',
            password=generate_password_hash('password123'),
            phone='1234567890',
            roll_number='EN001',
            division='A'
        )
        db.session.add(user)
        db.session.commit()
        print('Database initialized and test user created.')
    else:
        print('Database already initialized.')
