import os
import secrets
from datetime import datetime, timedelta
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.utils import secure_filename
#from werkzeug.security import check_password_hash, generate_password_hash
from helpers import signin_required
from models import db, Admin, Course, Event, Assignment, UserCourse, CourseMaterial, MaterialAnswer, StudentSubmission, Progress, Student, QuizResult
from sqlalchemy import exists, case, func, and_, or_, literal
from datetime import datetime


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = secrets.token_hex(32)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Supabase PostgreSQL config
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres.smqsrsogtfllwuxwsuhy:T%40limon2001@aws-0-eu-central-1.pooler.supabase.com:6543/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


#if the user is not logged in
@app.route("/")
def signin_post():
    return render_template("signin.html")

#when the user is logged in
@app.route("/home")
@signin_required
def home():
    return render_template("home.html")

#logging in the user
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")  # Get the role from form

        if not username or not password:
            flash("Please enter both username and password", "danger")
            return redirect("/signin")

        # Student login
        if role == 'student':
            student = Student.query.filter_by(student_number=username).first()
            if student and student.password == password:
                session["user_id"] = student.id
                flash("Welcome Back!", "success")
                return redirect("/home")
        
        # Admin login
        else:
            admin = Admin.query.filter_by(admin_number=username).first()
            if admin and admin.password == password:
                session["admin_id"] = admin.id
                session["role"] = admin.role
                flash("Welcome Back!", "success")
                return redirect("/home")

        flash("Invalid username or password", "danger")
        return redirect("/signin")
    
    # GET request - show appropriate form based on role parameter
    return render_template("signin.html")

@app.route("/logout")
@signin_required
def logout():
    session.clear()
    return redirect("/")

@app.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form.get("username")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not username or not new_password or not confirm_password:
            flash("Must fill all fields", "danger")
            return render_template("forgot.html")
        
        if new_password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template("forgot.html")

        student = Student.query.filter_by(student_number=username).first()
        admin = Admin.query.filter_by(admin_number=username).first()

        if student:
            student.password = new_password
            db.session.commit()
            flash("Password updated successfully", "success")
            return redirect("/signin")

        if admin:
            admin.password = new_password
            db.session.commit()
            flash("Password updated successfully", "success")
            return redirect("/signin")

        flash("User not found", "danger")
        return redirect("/forgot")
    return render_template("forgot.html")

@app.route("/dashboard")
@signin_required
def dashboard():
    user_id = session.get("user_id")

    my_courses = db.session.query(
        Course.id.label('course_id'),  # Get the course ID instead of title
        Course.title,
        Course.instructor,
        UserCourse.progress
    ).join(
        UserCourse, UserCourse.course_id == Course.id
    ).filter(
        UserCourse.user_id == user_id
    ).all()

    # Get just the course IDs for the upcoming events query
    course_ids = [course.course_id for course in my_courses]  # Now using actual IDs

    upcoming_events = []
    if course_ids:
        upcoming_events = (
            db.session.query(Event.title, Event.event_date, Course.title.label('course_title'))
            .join(Course, Event.course_id == Course.id)
            .filter(Event.course_id.in_(course_ids), Event.event_date >= datetime.now())
            .order_by(Event.event_date.asc())
            .all()
        )

    all_courses = Course.query.order_by(Course.title).all()

    return render_template("dashboard.html", my_courses=my_courses, all_courses=all_courses, upcoming_events=upcoming_events)


@app.route("/calendar")
@signin_required
def calendar():
    # Get today's date and set the date range (today to 30 days from now)
    today = datetime.now()
    start_date = today
    end_date = today + timedelta(days=30)

    # Get assignments due within the next 30 days
    assignments = db.session.query(
        Assignment.name.label("title"),
        Assignment.due_date.label("event_date"),
        Assignment.course_id,
        literal("assignment").label("type")
    ).filter(
        Assignment.due_date >= start_date,
        Assignment.due_date <= end_date
    )

    # Get materials uploaded within the next 30 days
    materials = db.session.query(
        CourseMaterial.title.label("title"),
        CourseMaterial.course_id,
        literal("material").label("type")
    ).filter()

    # Combine assignments and materials, then sort them by date
    assignments_list = assignments.all()
    materials_list = materials.all()

    events = assignments_list + materials_list
    events.sort(key=lambda e: e.event_date)

    # Assume you have access to current user's enrolled courses
    course_ids = [course.course_id for course in materials] 
    upcoming_events = []
    if course_ids:
        upcoming_events = (
            db.session.query(Event.title, Event.event_date, Course.title.label('course_title'))
            .join(Course, Event.course_id == Course.id)
            .filter(Event.course_id.in_(course_ids), Event.event_date >= datetime.now())
            .order_by(Event.event_date.asc())
            .all()
        )

    # Get all course titles mapped by course ID
    courses = db.session.query(Course).all()
    course_titles = {course.id: course.title for course in courses}

    # Prepare event data for the template
    event_data = [
        {
            "name": event.title,
            "date": event.event_date,
            "course": course_titles.get(event.course_id, "General"),
            "type": event.type
        }
        for event in events
    ]

    # Render the calendar with all events
    return render_template("calendar.html", upcoming_events=upcoming_events, events=event_data)


@app.route("/courses", methods=["GET", "POST"])
@signin_required
def courses():
    user_id = session["user_id"]

    if request.method == "POST":
        course_id = request.form.get("course_id")
        action = request.form.get("action")

        if not course_id or not action:
            flash("Missing required parameters", "danger")
            return redirect(url_for("courses"))

        try:
            course_id = int(course_id)
        except ValueError:
            flash("Invalid course ID format", "danger")
            return redirect(url_for("courses"))

        course = Course.query.get(course_id)
        if not course:
            flash("Course not found", "danger")
            return redirect(url_for("courses"))

        if action == "add":
            already_enrolled = UserCourse.query.filter_by(user_id=user_id, course_id=course_id).first()
            if already_enrolled:
                flash("You are already enrolled in this course", "info")
            else:
                new_enrollment = UserCourse(user_id=user_id, course_id=course_id, progress=0)
                db.session.add(new_enrollment)
                db.session.commit()
                flash("Successfully enrolled in course!", "success")

        elif action == "remove":
            UserCourse.query.filter_by(user_id=user_id, course_id=course_id).delete()
            db.session.commit()
            flash("Course removed successfully", "info")

        else:
            flash("Invalid action requested", "danger")

        return redirect(url_for("courses"))

    # GET request
    courses = db.session.query(
        Course.id,
        Course.title,
        Course.instructor,
        exists().where(UserCourse.user_id == user_id).where(UserCourse.course_id == Course.id).label("is_enrolled")
    ).order_by(Course.title).all()

    return render_template("courses.html", courses=courses)


@app.route("/mycourses")
@signin_required
def mycourses():
    user_id = session["user_id"]

    my_courses = db.session.query(
        Course.id.label("course_id"),
        Course.title,
        Course.instructor,
        UserCourse.progress
    ).join(UserCourse, UserCourse.course_id == Course.id
    ).filter(UserCourse.user_id == user_id
    ).order_by(Course.title).all()

    course_ids = [course.course_id for course in my_courses]

    events_by_course = {}
    if course_ids:
        events = Event.query.filter(
            Event.course_id.in_(course_ids),
            Event.event_date >= db.func.now()
        ).order_by(Event.event_date).all()

        for course_id in course_ids:
            events_by_course[course_id] = [e for e in events if e.course_id == course_id]

    return render_template("mycourses.html", my_courses=my_courses, events=events_by_course)


@app.route("/progress")
@signin_required
def progress():
    user_id = session.get("user_id") or session.get("admin_id")
    
    if not user_id:
        flash("Please log in to view this page", "danger")
        return redirect(url_for('signin'))

    # Overall progress statistics
    progress_data = db.session.query(
        func.count(UserCourse.id).label("total_courses"),
        func.sum(case(
            (UserCourse.progress == 100, 1),  
            else_=0
        )).label("completed_courses"),
        func.avg(UserCourse.progress).label("avg_progress")
    ).filter(UserCourse.user_id == user_id).first()
    # Progress by course
    courses_progress = db.session.query(
        Course.title,
        UserCourse.progress
    ).join(UserCourse, UserCourse.course_id == Course.id
    ).filter(UserCourse.user_id == user_id
    ).order_by(Course.title).all()

    return render_template(
        "progress.html",
        progress_data=progress_data,
        courses_progress=courses_progress
    )


@app.route("/grades")
@signin_required
def grades():
    user_id = session["user_id"]
    try:
        # Get grades
        grades = db.session.query(
            Course.title,
            Assignment.name.label("assignment"),
            Assignment.grade,
            Assignment.due_date
        ).join(UserCourse, UserCourse.course_id == Assignment.course_id
        ).join(Course, Course.id == Assignment.course_id
        ).filter(UserCourse.user_id == user_id
        ).order_by(Assignment.due_date.desc()).all()

        total_assignments = len(grades)
        average_grade = (
            sum(g.grade for g in grades) / total_assignments
            if total_assignments > 0 else 0
        )

        return render_template(
            "grades.html",
            grades=grades,
            total_assignments=total_assignments,
            average_grade=average_grade
        )
    except Exception as e:
        flash("An error occurred while loading grades", "danger")
        return redirect("/dashboard")


@app.route("/profile")
@signin_required
def profile():
    user_id = session.get("user_id")
    admin_id = session.get("admin_id")

    user = Student.query.get(user_id) if user_id else None
    admin = Admin.query.get(admin_id) if admin_id else None

    enrolled_courses = []
    quiz_results = []

    if user_id:
        # Student-specific data
        enrolled_courses = db.session.query(
            Course.title,
            UserCourse.progress,
            db.session.query(func.max(QuizResult.taken_at)).filter(
                QuizResult.user_id == user_id,
                QuizResult.quiz_name.ilike(f"%{Course.title}%")
            ).label("last_activity")
        ).join(UserCourse, UserCourse.course_id == Course.id
        ).filter(UserCourse.user_id == user_id
        ).order_by(Course.title).all()

        quiz_results = QuizResult.query.filter_by(user_id=user_id).order_by(QuizResult.taken_at.desc()).limit(5).all()

    return render_template(
        "profile.html",
        user=user,
        admin=admin,
        enrolled_courses=enrolled_courses,
        quiz_results=quiz_results,
        student=user
    )

@app.route("/updateprofile", methods=["POST"])
@signin_required
def update_profile():
    user_id = session.get("user_id")
    admin_id = session.get("admin_id")
    
    profile_pic = request.files.get("profile_pic")
    email = request.form.get("email")
    username = request.form.get("username")

    try:
        if user_id:
            # Update student profile
            student = Student.query.get(user_id)
            if profile_pic and profile_pic.filename != '':
                if allowed_file(profile_pic.filename):
                    # Secure the filename and make it unique
                    filename = secure_filename(profile_pic.filename)
                    unique_filename = f"student_{user_id}_{filename}"
                    save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    
                    # Save the file
                    profile_pic.save(save_path)
                    
                    # Delete old profile picture if exists
                    if student.profile_pic:
                        old_file = os.path.join(app.config['UPLOAD_FOLDER'], student.profile_pic)
                        if os.path.exists(old_file):
                            os.remove(old_file)
                    
                    student.profile_pic = unique_filename
                else:
                    flash("Invalid file type. Allowed types: png, jpg, jpeg, gif", "danger")
                    return redirect("/profile")
            
            student.email = email
            student.student_number = username
            
        elif admin_id:
            # Update admin profile
            admin = Admin.query.get(admin_id)
            if profile_pic and profile_pic.filename != '':
                if allowed_file(profile_pic.filename):
                    # Secure the filename and make it unique
                    filename = secure_filename(profile_pic.filename)
                    unique_filename = f"admin_{admin_id}_{filename}"
                    save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    
                    # Save the file
                    profile_pic.save(save_path)
                    
                    # Delete old profile picture if exists
                    if admin.profile_pic:
                        old_file = os.path.join(app.config['UPLOAD_FOLDER'], admin.profile_pic)
                        if os.path.exists(old_file):
                            os.remove(old_file)
                    
                    admin.profile_pic = unique_filename
                else:
                    flash("Invalid file type. Allowed types: png, jpg, jpeg, gif", "danger")
                    return redirect("/profile")
            
            admin.email = email
            admin.admin_number = username
        
        db.session.commit()
        flash("Profile updated successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating profile: {str(e)}", "danger")

    return redirect("/profile")

@app.route("/changepassword", methods=["POST"])
@signin_required
def change_password():
    user_id = session.get("user_id")
    admin_id = session.get("admin_id")
    
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if user_id:
        user = Student.query.get(user_id)
    elif admin_id:
        user = Admin.query.get(admin_id)
    else:
        flash("User not found", "danger")
        return redirect("/profile")

    # Compare plain text passwords directly
    if user.password != current_password:
        flash("Current password is incorrect", "danger")
        return redirect("/profile")

    if new_password != confirm_password:
        flash("New passwords don't match", "danger")
        return redirect("/profile")

    try:
        # Store plain text password
        user.password = new_password
        db.session.commit()
        flash("Password changed successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error changing password: {str(e)}", "danger")

    return redirect("/profile")

@app.route("/students")
@signin_required
def my_students():
    admin_id = session.get("admin_id")
    
    # Get admin's courses
    my_courses = Course.query.filter(Course.instructor == str(admin_id)).all()
    if not my_courses:
        flash("No courses assigned to you yet", "info")
        return redirect(url_for("home"))

    # Handle filters
    course_id = request.args.get('course_id', type=int)
    search = request.args.get('search', '').strip()

    # Query students with progress and quiz stats
    query = (
        db.session.query(
            Student,
            UserCourse.progress,
            Course.title.label('course_title'),
            Course.id.label('course_id'),
            func.count(QuizResult.id).label('quiz_count'),
            func.coalesce(func.avg(QuizResult.score), 0.0).label('avg_score')  
        )
        .join(UserCourse, UserCourse.user_id == Student.id)
        .join(Course, UserCourse.course_id == Course.id)
        .outerjoin(QuizResult, and_(
            QuizResult.user_id == Student.id,
            QuizResult.quiz_name == Course.title  
        ))
        .filter(Course.instructor == str(admin_id))
        .group_by(Student.id, UserCourse.progress, Course.title, Course.id)
    )

    # Apply filters
    if course_id:
        query = query.filter(Course.id == course_id)
    if search:
        query = query.filter(or_(
            Student.student_number.ilike(f"%{search}%"),
            Student.first_name.ilike(f"%{search}%"),
            Student.last_name.ilike(f"%{search}%")
        ))

    students_data = query.order_by(Student.last_name).all()

    return render_template(
        "students.html",
        students=students_data,
        courses=my_courses,
        selected_course=course_id,
        search_term=search
    )


@app.route("/admincourses", methods=['GET', 'POST'])
@signin_required
def admin_courses():
    admin_id = session.get("admin_id")
    
    # Handle course assignment form submission
    if request.method == 'POST':
        selected_courses = request.form.getlist('courses')
        
        # Clear existing assignments (corrected filter)
        Course.query.filter(Course.instructor == str(admin_id))
        
        # Set new assignments
        if selected_courses:
            Course.query.filter(Course.id.in_(selected_courses)).update(
                {'instructor': admin_id}, 
                synchronize_session=False
            )
            db.session.commit()
            flash("Your course assignments have been updated", "success")
        else:
            flash("You are no longer assigned to any courses", "warning")
        
        return redirect(url_for('admin_courses'))
    
    # Get all available courses and current assignments
    all_courses = Course.query.order_by(Course.title).all()  # Added ordering
    my_courses = Course.query.filter(Course.instructor == str(admin_id)).order_by(Course.title).all()
    
    # Get students for currently selected course
    selected_course_id = request.args.get('course_id', type=int)
    students = []
    
    if selected_course_id:
        students = db.session.query(
            Student,
            UserCourse.progress
        ).join(
            UserCourse, UserCourse.user_id == Student.id
        ).filter(
            UserCourse.course_id == selected_course_id
        ).order_by(
            Student.last_name,
            Student.first_name
        ).all()
    
    return render_template("admincourses.html",
                         all_courses=all_courses,
                         my_courses=my_courses,
                         students=students,
                         selected_course_id=selected_course_id)


@app.route("/content", methods=['GET', 'POST'])
@signin_required
def content_management():
    if not session.get('admin_id'):
        flash('Admin login required', 'danger')
        return redirect(url_for('signin'))

    if request.method == 'POST':
        # Course Material Upload
        if 'material_submit' in request.form:
            course_id = request.form.get('course_id')
            title = request.form.get('title')
            content = request.form.get('content')
            
            if not all([course_id, title, content]):
                flash('Please fill all material fields', 'danger')
            else:
                file_path = None
                if 'file' in request.files:
                    file = request.files['file']
                    if file.filename != '':
                        filename = secure_filename(file.filename)
                        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                        file_path = os.path.join(UPLOAD_FOLDER, filename)
                        file.save(file_path)
                
                new_material = CourseMaterial(
                    course_id=course_id,
                    title=title,
                    content=content,
                    file_path=file_path
                )
                db.session.add(new_material)
                db.session.commit()
                flash('Material uploaded!', 'success')

        # Assignment Creation
        elif 'assignment_submit' in request.form:
            course_id = request.form.get('course_id')
            name = request.form.get('name')
            grade = request.form.get('grade')
            due_date = request.form.get('due_date')
            answer_key = request.form.get('answer_key')
            
            if not all([course_id, name, grade, due_date, answer_key]):
                flash('Please fill all assignment fields', 'danger')
            else:
                new_assignment = Assignment(
                    course_id=course_id,
                    name=name,
                    grade=grade,
                    due_date=datetime.strptime(due_date, '%Y-%m-%d'),
                    answer_key=answer_key
                )
                db.session.add(new_assignment)
                db.session.commit()
                flash('Assignment created!', 'success')

        # Handle deletions
        elif 'delete_material' in request.form:
            material_id = request.form.get('material_id')
            material = CourseMaterial.query.get(material_id)
            if material:
                db.session.delete(material)
                db.session.commit()
                flash('Material deleted', 'success')

        elif 'delete_assignment' in request.form:
            assignment_id = request.form.get('assignment_id')
            assignment = Assignment.query.get(assignment_id)
            if assignment:
                db.session.delete(assignment)
                db.session.commit()
                flash('Assignment deleted', 'success')

    # Get all data for display
    courses = Course.query.all()
    materials = CourseMaterial.query.all()
    assignments = Assignment.query.all()

    return render_template('content.html',
                        courses=courses,
                        materials=materials,
                        assignments=assignments)

if __name__ == "__main__":
    app.run(debug=True)