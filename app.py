import os
from functools import wraps
from flask import Flask, render_template, url_for, redirect, flash, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Subject, PYQ, UserPYQ, StudyPlanner, Activity
from dotenv import load_dotenv
import json
import uuid

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

# Database configuration: use DATABASE_URL (PostgreSQL) if available, otherwise fallback to SQLite
_database_url = os.getenv('DATABASE_URL')

if _database_url:
    # Render/Heroku still issues postgres:// URIs; SQLAlchemy 1.4+ requires postgresql://
    if _database_url.startswith('postgres://'):
        _database_url = _database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = _database_url
    print("Environment: Production (PostgreSQL)")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local.db'
    print("Environment: Development (SQLite fallback)")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Setup Image Uploads
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'profile_pics')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    """Decorator: only allows access if current_user.role == 'admin'. Returns 403 otherwise."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        # Fetch top 10 most recent activities acting as notifications natively
        notifs = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.timestamp.desc()).limit(10).all()
        # Evaluate actively polling unread count directly natively flawlessly dynamically securely seamlessly cleanly
        unread_count = Activity.query.filter_by(user_id=current_user.id, is_read=False).count()
        return dict(notifications=notifs, unread_count=unread_count)
    return dict(notifications=[], unread_count=0)

@app.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        roll_number = request.form.get('roll_number')
        division = request.form.get('division')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', 'error')
            return redirect(url_for('signup'))

        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            phone=phone,
            roll_number=roll_number,
            division=division
        )
        db.session.add(new_user)
        db.session.commit()
        
        # Create default subjects for new user
        default_subjects = [
            'Physics', 'Chemistry', 'Mechanics', 'Maths 2', 'IKS',
            'MPW', 'DTIL', 'BXE', 'BEE', 'Engineering Graphics'
        ]
        for sub_name in default_subjects:
            subject = Subject(name=sub_name, progress=0, owner=new_user)
            db.session.add(subject)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.', 'error')
            return redirect(url_for('login'))

        login_user(user, remember=remember)
        
        # Log activity
        activity = Activity(user_id=user.id, action='login')
        db.session.add(activity)
        db.session.commit()
        
        # Role-based redirection
        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

@app.route('/dashboard')
@login_required
def dashboard():
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    upcoming_tasks = StudyPlanner.query.filter_by(user_id=current_user.id, status='Pending').order_by(StudyPlanner.created_at.desc()).limit(3).all()
    activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.timestamp.desc()).all()
    
    total_subjects = len(subjects)
    num_completed_tasks = len([a for a in activities if a.action == 'completed_task'])
    num_completed_pyqs = len([a for a in activities if a.action == 'completed_pyq'])
    total_activities = len(activities)
    
    # Calculate simple streak for old widget if needed, or replace with score
    score = float((num_completed_tasks * 0.5) + (num_completed_pyqs * 1.0) + (total_activities * 0.1))
    study_rating = min(10.0, round(score, 1))
    
    recent_activities = activities[:5] if activities else []
    
    return render_template('dashboard.html', 
                           subjects=subjects, 
                           upcoming_tasks=upcoming_tasks, 
                           total_subjects=total_subjects,
                           completed_tasks=num_completed_tasks,
                           completed_pyqs=num_completed_pyqs,
                           study_rating=study_rating,
                           recent_activities=recent_activities)

@app.route('/subjects')
@login_required
def subjects():
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('subjects.html', subjects=subjects)

@app.route('/update_progress/<int:subject_id>', methods=['POST'])
@login_required
def update_progress(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    # Ensure the subject belongs to the current user
    if subject.user_id != current_user.id:
        flash('Unauthorized action.', 'error')
        return redirect(url_for('subjects'))
        
    try:
        new_progress = int(request.form.get('progress'))
        if 0 <= new_progress <= 100:
            subject.progress = new_progress
            db.session.commit()
            flash(f'Progress for {subject.name} updated!', 'success')
        else:
            flash('Progress must be between 0 and 100.', 'error')
    except (ValueError, TypeError):
        flash('Invalid progress value.', 'error')
        
    return redirect(url_for('subjects'))

@app.route('/planner')
@login_required
def planner():
    tasks = StudyPlanner.query.filter_by(user_id=current_user.id).order_by(StudyPlanner.created_at.desc()).all()
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('planner.html', tasks=tasks, subjects=subjects)

@app.route('/planner/add', methods=['POST'])
@login_required
def add_planner_task():
    subject = request.form.get('subject')
    topic = request.form.get('topic')
    priority = request.form.get('priority')
    notes = request.form.get('notes', '')
    
    if not subject or not topic or not priority:
        flash('Subject, Topic, and Priority are required.', 'error')
        return redirect(url_for('planner'))
        
    if priority not in ['High', 'Medium', 'Low']:
        flash('Invalid priority level.', 'error')
        return redirect(url_for('planner'))
        
    new_task = StudyPlanner(
        user_id=current_user.id,
        subject=subject,
        topic=topic,
        priority=priority,
        notes=notes,
        status='Pending'
    )
    db.session.add(new_task)
    
    # Log activity
    activity = Activity(user_id=current_user.id, action='added_task')
    db.session.add(activity)
    
    db.session.commit()
    
    flash('Task added to planner!', 'success')
    return redirect(url_for('planner'))

@app.route('/planner/toggle/<int:task_id>', methods=['POST'])
@login_required
def toggle_planner_task(task_id):
    task = StudyPlanner.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('Unauthorized action.', 'error')
        return redirect(url_for('planner'))
        
    if task.status == 'Pending':
        task.status = 'Completed'
        # Log activity
        activity = Activity(user_id=current_user.id, action='completed_task')
        db.session.add(activity)
    else:
        task.status = 'Pending'
        
    db.session.commit()
    return redirect(url_for('planner'))

@app.route('/activity')
@login_required
def activity():
    activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.timestamp).all()
    
    bar_data = {}
    pie_data = {}
    
    num_completed_tasks = 0
    num_completed_pyqs = 0
    total_activities = len(activities)
    
    for act in activities:
        date_str = act.timestamp.strftime('%Y-%m-%d')
        bar_data[date_str] = bar_data.get(date_str, 0) + 1
        pie_data[act.action] = pie_data.get(act.action, 0) + 1
        
        if act.action == 'completed_task':
            num_completed_tasks += 1
        elif act.action == 'completed_pyq':
            num_completed_pyqs += 1
            
    # Calculate Rating (0 to 10)
    score = (num_completed_tasks * 0.5) + (num_completed_pyqs * 1.0) + (total_activities * 0.1)
    score = min(10.0, round(score, 1))
    
    if score >= 8:
        emoji = "😄"
    elif score >= 5:
        emoji = "🙂"
    elif score >= 3:
        emoji = "😐"
    else:
        emoji = "😴"
        
    return render_template(
        'activity.html', 
        bar_data=json.dumps(bar_data), 
        pie_data=json.dumps(pie_data),
        rating_score=score,
        rating_emoji=emoji
    )

@app.route('/account')
@login_required
def account():
    return render_template('account.html')

@app.route('/upload_profile_pic', methods=['POST'])
@login_required
def upload_profile_pic():
    if 'profile_pic' not in request.files:
        flash('No file part provided.', 'error')
        return redirect(url_for('account'))
        
    file = request.files['profile_pic']
    
    if file.filename == '':
        flash('No image selected for uploading.', 'error')
        return redirect(url_for('account'))
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Gen strict unique identifier to prevent browser caching & collisions
        unique_filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save payload
        file.save(file_path)
        
        # Optionally remove old profile pic locally if you want to save space
        if current_user.profile_pic:
            old_path = os.path.join('static', current_user.profile_pic)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass
        
        # Update user record uniquely accessible via static rendering bounds
        current_user.profile_pic = f"uploads/profile_pics/{unique_filename}"
        db.session.commit()
        
        # Log telemetry naturally
        activity = Activity(user_id=current_user.id, action='updated_avatar')
        db.session.add(activity)
        db.session.commit()
        
        flash('Profile picture successfully updated!', 'success')
        return redirect(url_for('account'))
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif, webp', 'error')
        return redirect(url_for('account'))
@app.route('/pyqs')
@login_required
def pyqs():
    subject_filter = request.args.get('subject')
    
    # Get all subjects that have PYQs for the filter UI
    available_subjects = db.session.query(PYQ.subject).distinct().all()
    available_subjects = [s[0] for s in available_subjects]
    
    if subject_filter:
        pyqs_list = PYQ.query.filter_by(subject=subject_filter).all()
    else:
        pyqs_list = PYQ.query.all()
        
    # Get user interactions
    user_interactions = UserPYQ.query.filter_by(user_id=current_user.id).all()
    interactions_dict = {i.pyq_id: i.status for i in user_interactions}
        
    return render_template('pyqs.html', pyqs=pyqs_list, subjects=available_subjects, current_subject=subject_filter, interactions=interactions_dict)

@app.route('/pyq/<int:pyq_id>/interaction', methods=['POST'])
@login_required
def pyq_interaction(pyq_id):
    status = request.form.get('status')
    if status not in ['completed', 'important']:
        flash('Invalid status.', 'error')
        return redirect(url_for('pyqs'))
        
    interaction = UserPYQ.query.filter_by(user_id=current_user.id, pyq_id=pyq_id).first()
    
    if interaction:
        if interaction.status == status:
            # Toggle off
            db.session.delete(interaction)
            db.session.commit()
            flash('Interaction removed.', 'success')
        else:
            # Update to new status
            interaction.status = status
            
            # Log activity if completed
            if status == 'completed':
                activity = Activity(user_id=current_user.id, action='completed_pyq')
                db.session.add(activity)
                
            db.session.commit()
            flash(f'Marked as {status}.', 'success')
            
            # Auto-generate planner task
            pyq = PYQ.query.get(pyq_id)
            if pyq:
                action = "Revise" if status == 'important' else "Review Completed"
                new_task = StudyPlanner(
                    user_id=current_user.id,
                    subject=pyq.subject,
                    topic=f"{action} {pyq.subject} {pyq.year} {pyq.type}",
                    priority="High" if status == 'important' else "Medium",
                    notes=f"Auto-generated tracking for marking paper as '{status}'.",
                    status="Pending"
                )
                db.session.add(new_task)
                db.session.commit()
    else:
        # Create new interaction
        new_interaction = UserPYQ(user_id=current_user.id, pyq_id=pyq_id, status=status)
        db.session.add(new_interaction)
        
        # Log activity if completed
        if status == 'completed':
            activity = Activity(user_id=current_user.id, action='completed_pyq')
            db.session.add(activity)
            
        db.session.commit()
        flash(f'Marked as {status}.', 'success')
        
        # Auto-generate planner task
        pyq = PYQ.query.get(pyq_id)
        if pyq:
            action = "Revise" if status == 'important' else "Review Completed"
            new_task = StudyPlanner(
                user_id=current_user.id,
                subject=pyq.subject,
                topic=f"{action} {pyq.subject} {pyq.year} {pyq.type}",
                priority="High" if status == 'important' else "Medium",
                notes=f"Auto-generated tracking for marking paper as '{status}'.",
                status="Pending"
            )
            db.session.add(new_task)
            db.session.commit()
        
    # Redirect back preserving the subject filter if possible
    subject_filter = request.form.get('current_subject')
    if subject_filter:
        return redirect(url_for('pyqs', subject=subject_filter))
    return redirect(url_for('pyqs'))

@app.route('/mark_all_read', methods=['POST'])
@login_required
def mark_all_read():
    Activity.query.filter_by(user_id=current_user.id, is_read=False).update({Activity.is_read: True})
    db.session.commit()
    return {'status': 'success'}

# ── Admin Routes ──────────────────────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_dashboard():
    users_count     = User.query.count()
    tasks_count     = StudyPlanner.query.count()
    pyqs_count      = PYQ.query.count()
    activities_count = Activity.query.count()
    return render_template('admin/dashboard.html',
                           users_count=users_count,
                           tasks_count=tasks_count,
                           pyqs_count=pyqs_count,
                           activities_count=activities_count)

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.order_by(User.id.asc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    activities = Activity.query.all()
    activity_summary = {}
    for act in activities:
        activity_summary[act.action] = activity_summary.get(act.action, 0) + 1
    return render_template('admin/analytics.html', activity_summary=activity_summary)

@app.route('/admin/resources')
@admin_required
def admin_resources():
    return render_template('admin/resources.html')

@app.route('/admin/settings')
@admin_required
def admin_settings():
    env = 'Production' if os.getenv('DATABASE_URL') else 'Development (SQLite)'
    return render_template('admin/settings.html', env=env)

@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash("You cannot delete your own account!", "danger")
        return redirect(url_for('admin_users'))
    
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f"User {user.name} deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user: {str(e)}", "danger")
        
    return redirect(url_for('admin_users'))

# ── Error Handlers ────────────────────────────────────────────────────────────

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

# Initialize database tables on startup.
# Running inside app_context() here ensures this works under Gunicorn/multi-worker environments
# without relying on the __main__ block (which is never reached under Gunicorn).
with app.app_context():
    db.create_all()
    # Safely add 'role' column to existing databases that predate this migration
    # Note: "user" is a reserved keyword in PostgreSQL, so we quote it.
    from sqlalchemy import text
    try:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT \'student\''))
        db.session.commit()
    except Exception:
        db.session.rollback()  # Column already exists or table doesn't exist — safe to ignore

    # Initialize default admin if none exists
    admin_exists = User.query.filter_by(role='admin').first()
    if not admin_exists:
        try:
            default_admin = User(
                name="Admin",
                email="admin@studysync.com",
                password=generate_password_hash("admin123"),
                role="admin"
            )
            db.session.add(default_admin)
            db.session.commit()
            print("[OK] Default admin created: admin@studysync.com / admin123")
        except Exception as e:
            db.session.rollback()
            print(f"[Error] Failed to create default admin: {e}")
    else:
        print("[OK] Admin exists in database.")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
