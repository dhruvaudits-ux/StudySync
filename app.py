import os
import cloudinary
import cloudinary.uploader
from functools import wraps
from flask import Flask, render_template, url_for, redirect, flash, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Subject, PYQ, UserPYQ, StudyPlanner, Activity, Attendance, Resource
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta

load_dotenv()

# Cloudinary Configuration
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME', 'duxkzbatg'),
    api_key=os.getenv('CLOUDINARY_API_KEY', '429586186666547'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET', 'Mi3yz6c_yRRS6aq_5gQ_6peIIpg')
)

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
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        print(f"[Login Attempt] Email: {email}")
        user = User.query.filter_by(email=email).first()

        if not user:
            print(f"[Login] User not found: {email}")
            flash('Please check your login details and try again.', 'error')
            return redirect(url_for('login'))

        if not check_password_hash(user.password, password):
            print(f"[Login] Invalid password for: {email}")
            flash('Please check your login details and try again.', 'error')
            return redirect(url_for('login'))

        login_user(user, remember=remember)
        print(f"[Login] Success: {email} (ID: {user.id}, Role: {user.role})")
        
        # Log activity
        activity = Activity(user_id=user.id, action='login')
        db.session.add(activity)
        db.session.commit()
        
        # Role-based redirection
        if user.role == 'admin':
            print(f"[Login] Redirecting Admin to /admin/dashboard")
            return redirect(url_for('admin_dashboard'))
        print(f"[Login] Redirecting Student to /dashboard")
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
    print(f"DEBUG: current_user.role = {current_user.role}")
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
        
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

@app.route('/resources')
@login_required
def resources():
    subject_filter = request.args.get('subject')
    type_filter = request.args.get('type')
    
    query = Resource.query
    if subject_filter:
        query = query.filter_by(subject=subject_filter)
    if type_filter:
        query = query.filter_by(type=type_filter)
        
    all_resources = query.order_by(Resource.upload_date.desc()).all()
    # For the filter dropdown:
    subjects = db.session.query(Resource.subject).distinct().all()
    subjects = [s[0] for s in subjects]
    
    return render_template('resources.html', resources=all_resources, subjects=subjects)

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

@app.route('/planner/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_planner_task(task_id):
    task = StudyPlanner.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('Unauthorized action.', 'error')
        return redirect(url_for('planner'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted from planner.', 'success')
    return redirect(url_for('planner'))

@app.route('/activity')
@login_required
def activity():
    # Fetch last 7 days of activity for the timeline
    today = datetime.utcnow().date()
    seven_days_ago = today - timedelta(days=6)
    
    activities = Activity.query.filter(
        Activity.user_id == current_user.id,
        Activity.timestamp >= seven_days_ago
    ).order_by(Activity.timestamp).all()
    
    # Initialize timeline with 0s for the last 7 days
    bar_data = {}
    for i in range(7):
        day = seven_days_ago + timedelta(days=i)
        bar_data[day.strftime('%Y-%m-%d')] = 0
        
    pie_data = {}
    
    # Fetch ALL activities for the rating and distribution
    all_user_activities = Activity.query.filter_by(user_id=current_user.id).all()
    
    num_completed_tasks = 0
    num_completed_pyqs = 0
    total_activities = len(all_user_activities)
    
    for act in all_user_activities:
        # Update pie data (distribution)
        action_label = act.action.replace('_', ' ').title()
        pie_data[action_label] = pie_data.get(action_label, 0) + 1
        
        # Update rating counters
        if act.action == 'completed_task':
            num_completed_tasks += 1
        elif act.action == 'completed_pyq':
            num_completed_pyqs += 1
            
        # Update timeline if within range
        date_str = act.timestamp.strftime('%Y-%m-%d')
        if date_str in bar_data:
            bar_data[date_str] += 1
            
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
        try:
            # Check file size (limit to 5MB for avatars)
            file.seek(0, os.SEEK_END)
            file_length = file.tell()
            if file_length > 5 * 1024 * 1024:
                flash('File too large. Max size is 5MB.', 'error')
                return redirect(url_for('account'))
            file.seek(0)

            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(file, folder="avatars/")
            avatar_url = upload_result.get('secure_url')
            
            # Update user record with the Cloudinary URL
            current_user.avatar_url = avatar_url
            db.session.commit()
            
            # Log telemetry
            activity = Activity(user_id=current_user.id, action='updated_avatar')
            db.session.add(activity)
            db.session.commit()
            
            flash('Profile picture successfully updated!', 'success')
        except Exception as e:
            flash(f'Error uploading to Cloudinary: {str(e)}', 'error')
        
        return redirect(url_for('account'))
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif, webp', 'error')
        return redirect(url_for('account'))
@app.route('/delete_avatar', methods=['POST'])
@login_required
def delete_avatar():
    if current_user.avatar_url:
        # We don't necessarily need to delete from Cloudinary here for simple cleanup,
        # but we definitely reset the URL in DB.
        current_user.avatar_url = None
        db.session.commit()
        flash('Profile picture removed.', 'success')
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
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    print(f"DEBUG: admin_dashboard accessed by {current_user.email} (Role: {current_user.role})")
    users_count     = User.query.count()
    students_count   = User.query.filter_by(role='student').count()
    tasks_count     = StudyPlanner.query.count()
    pyqs_count      = PYQ.query.count()
    activities_count = Activity.query.count()
    return render_template('admin/dashboard.html',
                           users_count=users_count,
                           students_count=students_count,
                           tasks_count=tasks_count,
                           pyqs_count=pyqs_count,
                           activities_count=activities_count)

@app.route('/admin/users')
@admin_required
def admin_users():
    users = User.query.order_by(User.id.asc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/upload', methods=['GET', 'POST'])
@admin_required
def admin_upload():
    if request.method == 'POST':
        title = request.form.get('title')
        subject = request.form.get('subject')
        file_type = request.form.get('type')
        file = request.files.get('file')

        if not all([title, subject, file_type, file]):
            flash("All fields are required!", "danger")
            return redirect(request.url)

        if file and file.filename.lower().endswith('.pdf'):
            try:
                # Check file size (limit to 10MB for PDFs)
                file.seek(0, os.SEEK_END)
                file_length = file.tell()
                if file_length > 10 * 1024 * 1024:
                    flash('File too large. Max size is 10MB.', 'danger')
                    return redirect(request.url)
                file.seek(0)

                # Upload to Cloudinary with resource_type="raw" for PDFs
                upload_result = cloudinary.uploader.upload(
                    file, 
                    folder="resources/",
                    resource_type="raw",
                    use_filename=True,
                    unique_filename=True
                )
                pdf_url = upload_result.get('secure_url')

                new_resource = Resource(
                    title=title,
                    subject=subject,
                    type=file_type,
                    pdf_url=pdf_url
                )
                db.session.add(new_resource)
                db.session.commit()
                
                # Log activity
                activity = Activity(user_id=current_user.id, action=f'uploaded_{file_type.lower()}')
                db.session.add(activity)
                db.session.commit()

                flash(f"Resource '{title}' uploaded successfully!", "success")
                return redirect(url_for('admin_dashboard'))
            except Exception as e:
                flash(f"Error uploading to Cloudinary: {str(e)}", "danger")
                return redirect(request.url)
        else:
            flash("Only PDF files are allowed!", "danger")
            return redirect(request.url)

    # Get distinct subjects for the dropdown
    subjects = db.session.query(Subject.name).distinct().all()
    subject_list = [s[0] for s in subjects] if subjects else ["General", "Maths", "Physics", "Chemistry"]
    return render_template('admin/upload.html', subjects=subject_list)


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
@app.route('/admin/users/toggle_role/<int:user_id>', methods=['POST'])
@admin_required
def toggle_user_role(user_id):
    if user_id == current_user.id:
        flash("You cannot change your own role!", "danger")
        return redirect(url_for('admin_users'))
    
    user = User.query.get_or_404(user_id)
    try:
        if user.role == 'admin':
            user.role = 'student'
        else:
            user.role = 'admin'
        db.session.commit()
        flash(f"User {user.name} role updated to {user.role}.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating role: {str(e)}", "danger")
        
    return redirect(url_for('admin_users'))

@app.route('/admin/resources')
@admin_required
def admin_resources():
    all_resources = Resource.query.order_by(Resource.upload_date.desc()).all()
    return render_template('admin/resources.html', resources=all_resources)

@app.route('/admin/resources/delete/<int:resource_id>', methods=['POST'])
@admin_required
def delete_resource(resource_id):
    resource = Resource.query.get_or_404(resource_id)
    try:
        db.session.delete(resource)
        db.session.commit()
        flash(f"Resource '{resource.title}' deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting resource: {str(e)}", "danger")
    return redirect(url_for('admin_resources'))

# ── Attendance Routes ─────────────────────────────────────────────────────────

@app.route('/admin/attendance', methods=['GET'])
@admin_required
def admin_attendance():
    # Admin selects division, date, lecture, subject
    selected_division = request.args.get('division')
    selected_date = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    selected_lecture = request.args.get('lecture', '1')
    selected_subject = request.args.get('subject', 'General')
    
    divisions = db.session.query(User.division).distinct().all()
    divisions = [d[0] for d in divisions if d[0]]

    students = []
    if selected_division:
        students = User.query.filter_by(role='student', division=selected_division).order_by(User.roll_number).all()

    # Get existing attendance for this specific session
    existing_records = {}
    if students and selected_date and selected_lecture:
        try:
            parsed_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            records = Attendance.query.filter_by(
                date=parsed_date, lecture=int(selected_lecture)
            ).all()
            existing_records = {r.student_id: r.status for r in records}
        except ValueError:
            pass

    return render_template('admin/attendance.html',
                           divisions=divisions,
                           students=students,
                           selected_division=selected_division,
                           selected_date=selected_date,
                           selected_lecture=selected_lecture,
                           selected_subject=selected_subject,
                           existing_records=existing_records)

@app.route('/admin/attendance/mark', methods=['POST'])
@admin_required
def mark_attendance():
    division = request.form.get('division')
    date_str = request.form.get('date')
    lecture_str = request.form.get('lecture')
    subject = request.form.get('subject')

    if not all([division, date_str, lecture_str, subject]):
        flash("Please provide all required fields.", "danger")
        return redirect(url_for('admin_attendance'))

    try:
        parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        parsed_lecture = int(lecture_str)
    except ValueError:
        flash("Invalid date or lecture format.", "danger")
        return redirect(url_for('admin_attendance', division=division))

    students = User.query.filter_by(role='student', division=division).all()
    
    for student in students:
        status = request.form.get(f"status_{student.id}")
        if status in ['Present', 'Absent']:
            # Check if record already exists
            record = Attendance.query.filter_by(
                student_id=student.id,
                date=parsed_date,
                lecture=parsed_lecture
            ).first()

            if record:
                record.status = status
            else:
                new_record = Attendance(
                    student_id=student.id,
                    date=parsed_date,
                    lecture=parsed_lecture,
                    subject=subject,
                    status=status
                )
                db.session.add(new_record)

    db.session.commit()
    flash(f"Attendance saved for Division {division} on {date_str}, Lecture {parsed_lecture}.", "success")
    
    return redirect(url_for('admin_attendance', 
                            division=division, 
                            date=date_str, 
                            lecture=lecture_str, 
                            subject=subject))

@app.route('/attendance')
@login_required
def attendance():
    if current_user.role == 'admin':
        return redirect(url_for('admin_attendance'))
        
    if current_user.role != 'student':
        flash("Access denied: This page is for students only.", "warning")
        return redirect(url_for('admin_dashboard'))
        
    records = Attendance.query.filter_by(student_id=current_user.id).order_by(Attendance.date.desc(), Attendance.lecture.desc()).all()
    
    total_classes = len(records)
    present_classes = sum(1 for r in records if r.status == 'Present')
    
    overall_percentage = 0
    if total_classes > 0:
        overall_percentage = round((present_classes / total_classes) * 100, 1)

    # Subject-wise stats
    subject_stats = {}
    for r in records:
        if r.subject not in subject_stats:
            subject_stats[r.subject] = {'total': 0, 'present': 0}
        
        subject_stats[r.subject]['total'] += 1
        if r.status == 'Present':
            subject_stats[r.subject]['present'] += 1
            
    for sub, stats in subject_stats.items():
        stats['percentage'] = round((stats['present'] / stats['total']) * 100, 1)

    return render_template('student/attendance.html', 
                           records=records, 
                           overall_percentage=overall_percentage,
                           total_classes=total_classes,
                           present_classes=present_classes,
                           subject_stats=subject_stats)

# ── Error Handlers ────────────────────────────────────────────────────────────

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

# Initialize database tables on startup.
# Running inside app_context() here ensures this works under Gunicorn/multi-worker environments
# without relying on the __main__ block (which is never reached under Gunicorn).
with app.app_context():
    db.create_all()
    # Database migrations & stabilization
    from sqlalchemy import text
    
    # 1. Core fields
    try:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT \'student\''))
        db.session.commit()
    except Exception:
        db.session.rollback()

    # 2. Cloudinary URL columns
    migration_columns = [
        ('user', 'avatar_url', 'VARCHAR(500)'),
        ('pyq', 'pdf_url', 'VARCHAR(500)'),
        ('resource', 'pdf_url', 'VARCHAR(500)')
    ]
    for table, col, col_type in migration_columns:
        try:
            db.session.execute(text(f'ALTER TABLE "{table}" ADD COLUMN {col} {col_type}'))
            db.session.commit()
        except Exception:
            db.session.rollback()

    # 3. Drop NOT NULL constraints for legacy fields (Cloudinary migration fix)
    # Note: PostgreSQL uses ALTER COLUMN ... DROP NOT NULL. SQLite does not support this easily.
    not_null_fixes = [
        ('user', 'profile_pic'),
        ('resource', 'filename'),
        ('pyq', 'file_name')
    ]
    for table, col in not_null_fixes:
        try:
            db.session.execute(text(f'ALTER TABLE "{table}" ALTER COLUMN {col} DROP NOT NULL'))
            db.session.commit()
            print(f"[OK] Dropped NOT NULL on {table}.{col}")
        except Exception as e:
            db.session.rollback()
            # Silence error if it's SQLite or already dropped
            if "ALTER" in str(e):
                print(f"[Info] Migration skipped for {table}.{col} (likely SQLite or already fixed)")
            else:
                print(f"[Warning] Failed to drop NOT NULL on {table}.{col}: {e}")

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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
