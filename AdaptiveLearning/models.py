from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_number = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    middle_name = db.Column(db.String)
    last_name = db.Column(db.String, nullable=False)
    date_of_birth = db.Column(db.Date)
    password = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    religion = db.Column(db.String, nullable=False)
    postal_address = db.Column(db.String, nullable=False)
    home_town = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    enrollment_date = db.Column(db.Date)
    status = db.Column(db.String)
    program_of_study = db.Column(db.String)
    year_of_study = db.Column(db.Integer)
    nationality = db.Column(db.String)
    parent_1_full_name = db.Column(db.String, nullable=False)
    parent_1_relationship = db.Column(db.String, nullable=False)
    parent_1_phone = db.Column(db.String, nullable=False)
    parent_1_email = db.Column(db.String)
    parent_2_full_name = db.Column(db.String)
    parent_2_relationship = db.Column(db.String)
    parent_2_phone = db.Column(db.String)
    parent_2_email = db.Column(db.String)

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_number = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String, nullable=False)
    middle_name = db.Column(db.String)
    last_name = db.Column(db.String, nullable=False)
    date_of_birth = db.Column(db.Date)
    password = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    religion = db.Column(db.String, nullable=False)
    postal_address = db.Column(db.String, nullable=False)
    home_town = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    role = db.Column(db.String, nullable=False)

class FeeStatement(db.Model):
    __tablename__ = 'fee_statement'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    person_id = db.Column(db.String, db.ForeignKey('student.id'), nullable=False)
    reference = db.Column(db.String, nullable=False, default='')
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String, nullable=False, default='')
    debit = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    credit = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    total = db.Column(db.Numeric(10, 2), default=0.00)

class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    person_id = db.Column(db.String, db.ForeignKey('student.id'), nullable=False)
    unit_code = db.Column(db.String, nullable=False)
    unit_description = db.Column(db.String, nullable=False)
    academic_hours = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    instructor = db.Column(db.String, nullable=False)

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)

class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    grade = db.Column(db.Numeric, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    answer_key = db.Column(db.Text)

class QuizResult(db.Model):
    __tablename__ = 'quiz_results'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    quiz_name = db.Column(db.String, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    taken_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

class UserCourse(db.Model):
    __tablename__ = 'user_courses'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    progress = db.Column(db.Integer, default=0)

class CourseMaterial(db.Model):
    __tablename__ = 'course_materials'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text)

class MaterialAnswer(db.Model):
    __tablename__ = 'material_answers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    material_id = db.Column(db.Integer, db.ForeignKey('course_materials.id'), nullable=False)
    question_number = db.Column(db.Integer, nullable=False)
    correct_answer = db.Column(db.String, nullable=False)
    max_points = db.Column(db.Integer, nullable=False)

class StudentSubmission(db.Model):
    __tablename__ = 'student_submissions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('course_materials.id'), nullable=False)
    file_path = db.Column(db.String, nullable=False)
    submission_date = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    score = db.Column(db.Integer)
    feedback = db.Column(db.Text)

class Progress(db.Model):
    __tablename__ = 'progress'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String, db.ForeignKey('students.id'), nullable=False)
    lesson = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)