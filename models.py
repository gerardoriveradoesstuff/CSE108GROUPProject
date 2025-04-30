from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Association table for many-to-many student enrollments
enrollments = db.Table('enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)  # unified primary key

    # Login-related fields
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'student' or 'teacher'

    # Profile fields for finance module
    email = db.Column(db.String(100), nullable=False, unique=True)

    # Relationships
    courses_enrolled = db.relationship('Course', secondary=enrollments, backref='students')
    courses_taught = db.relationship('Course', backref='teacher', foreign_keys='Course.teacher_id')
    deadlines = db.relationship('Deadline', back_populates='user', cascade="all, delete-orphan")
    transactions = db.relationship('Transaction', back_populates='user', lazy='dynamic')
    reports = db.relationship('Report', back_populates='user', cascade="all, delete-orphan")

    @validates('email')
    def validate_email(self, key, value):
        if not value or '@' not in value:
            raise ValueError("Invalid email address")
        return value


class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    time = db.Column(db.String(64), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Grade(db.Model):
    __tablename__ = 'grade'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    grade = db.Column(db.Integer)


class Deadline(db.Model):
    __tablename__ = 'deadline'
    id = db.Column(db.Integer, primary_key=True)
    assignment = db.Column(db.String(128), nullable=False)
    due_date = db.Column(db.String(64), nullable=False)

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course = db.relationship('Course', backref='deadlines')

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='deadlines')


class Transaction(db.Model):
    __tablename__ = 'transaction'
    transaction_id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    income = db.Column(db.Float, nullable=True, default=0.0)
    expense = db.Column(db.Float, nullable=True, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id', ondelete='SET NULL'))
    description = db.Column(db.String(255), nullable=True)

    user = db.relationship('User', back_populates='transactions')
    category = db.relationship('Category', back_populates='transactions')

    @validates('income', 'expense')
    def validate_amount(self, key, value):
        if value is not None and value < 0:
            raise ValueError("Amount cannot be negative")
        return value


class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    transactions = db.relationship('Transaction', back_populates='category', lazy='dynamic')

    @validates('name')
    def validate_name(self, key, value):
        if not value or len(value.strip()) == 0:
            raise ValueError("Category name cannot be empty")
        return value


class Report(db.Model):
    __tablename__ = 'report'
    report_id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', back_populates='reports')
