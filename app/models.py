from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_mentor(self):
        return self.role == 'mentor'

    def is_intern(self):
        return self.role == 'intern'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    mentor = db.relationship('User', backref='courses')
    presentation = db.relationship('CoursePresentation', uselist=False, backref='course')
    notes = db.relationship('CourseNotes', uselist=False, backref='course')
    quiz = db.relationship('CourseQuiz', uselist=False, backref='course')
    homework = db.relationship('CourseHomework', uselist=False, backref='course')

class CoursePresentation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

class CourseNotes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

class CourseQuiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    questions = db.Column(db.Text, nullable=False)  # JSON-encoded format
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

class CourseHomework(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instructions = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

class CourseProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    intern_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    presentation_viewed = db.Column(db.Boolean, default=False)
    quiz_passed = db.Column(db.Boolean, default=False)
    homework_submitted = db.Column(db.Boolean, default=False)
    submission_filename = db.Column(db.String(256), nullable=True)

    intern = db.relationship('User', backref='progress')
    course = db.relationship('Course', backref='progress')
