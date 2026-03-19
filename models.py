from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    roll_number = db.Column(db.String(20))
    division = db.Column(db.String(10))
    profile_pic = db.Column(db.String(255), nullable=True)
    # Role: 'student' (default) or 'admin'
    role = db.Column(db.String(20), nullable=False, default='student')

    # Relationship with Subject
    subjects = db.relationship('Subject', backref='owner', lazy=True, cascade="all, delete-orphan")
    
    # Relationship with UserPYQ
    pyq_interactions = db.relationship('UserPYQ', backref='user', lazy=True, cascade="all, delete-orphan")
    
    # Relationship with StudyPlanner
    planner_tasks = db.relationship('StudyPlanner', backref='user', lazy=True, cascade="all, delete-orphan")
    
    # Relationship with Activity
    activities = db.relationship('Activity', backref='user', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.name}>'

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    progress = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Subject {self.name}>'

class PYQ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(10), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<PYQ {self.subject} {self.year} {self.type}>'

class UserPYQ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pyq_id = db.Column(db.Integer, db.ForeignKey('pyq.id'), nullable=False)
    status = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f'<UserPYQ user:{self.user_id} pyq:{self.pyq_id} status:{self.status}>'

class StudyPlanner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<StudyPlanner {self.subject} - {self.topic}>'

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Activity {self.user_id} - {self.action}>'
