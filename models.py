from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Association table for many-to-many student enrollments
enrollments = db.Table('enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'student' or 'teacher'

    # For students and teachers
    courses_enrolled = db.relationship('Course', secondary=enrollments, backref='students')
    courses_taught = db.relationship('Course', backref='teacher', foreign_keys='Course.teacher_id')
    deadlines = db.relationship('Deadline', back_populates='user', cascade="all, delete-orphan")


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    time = db.Column(db.String(64), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    grade = db.Column(db.Integer)

class Deadline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment = db.Column(db.String(128), nullable=False)
    due_date = db.Column(db.String(64), nullable=False)

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course = db.relationship('Course', backref='deadlines')

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='deadlines')
