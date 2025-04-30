from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from models import db, User, Course, Grade
from forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from sqlalchemy.orm import joinedload
main = Blueprint('main', __name__)


@main.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists")
            return render_template("register.html", form=form)

        hashed_password = generate_password_hash(form.password.data)

        new_user = User(
            username=form.username.data,
            password=hashed_password,   # set the hashed password here
            role=form.role.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for("main.login"))

    return render_template("register.html", form=form)


@main.route("/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            if user.role == "student":
                return redirect(url_for("main.student_dashboard"))
            elif user.role == "teacher":
                return redirect(url_for("main.teacher_dashboard"))
        flash("Invalid credentials")
    return render_template("login.html", form=form)

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))

@main.route("/student")
@login_required
def student_dashboard():
    # this is lazy-loading. Didn't work because
    # current_user (student) is passed directly into templates. The session closes before the template tries to access it
    # all_courses = Course.query.all()
    # return render_template("student_dashboard.html", user=current_user, all_courses=all_courses)
    # re-fetch the user with all relationships eagerly loaded
    user = User.query.options(joinedload(User.courses_enrolled).joinedload(Course.teacher)).get(current_user.id)
    all_courses = Course.query.all()
    user = User.query.options(
        joinedload(User.courses_enrolled).joinedload(Course.teacher),
        joinedload(User.deadlines)
    ).get(current_user.id)

    return render_template("student_dashboard.html", user=user, all_courses=all_courses)


@main.route("/student/add/<int:course_id>", methods=["POST"])
@login_required
def add_course(course_id):
    """
    User.query.options(joinedload(...)) keeps user attached to the session and preloads courses_enrolled.
    not relying on current_user in a detached state.
    This avoids awkward cases where the session context is lost (e.g., after an admin page redirect or a redirect from another view).
    :param course_id:
    :return:
    """
    course = Course.query.get(course_id)

    # Eagerly load user with enrolled courses
    user = User.query.options(joinedload(User.courses_enrolled)).get(current_user.id)

    # Prevent double enrollment and check capacity
    if course and len(course.students) < course.capacity and course not in user.courses_enrolled:
        user.courses_enrolled.append(course)
        db.session.commit()

    return redirect(url_for("main.student_dashboard"))

@main.route("/student/drop/<int:course_id>", methods=["POST"])
@login_required
def drop_course(course_id):
    user = User.query.options(joinedload(User.courses_enrolled)).get(current_user.id)
    course = Course.query.get(course_id)
    if course and course in user.courses_enrolled:
        user.courses_enrolled.remove(course)
        db.session.commit()
    return redirect(url_for("main.student_dashboard"))

@main.route("/teacher")
@login_required
def teacher_dashboard():
    user = User.query.options(joinedload(User.courses_enrolled).joinedload(Course.teacher)).get(current_user.id)
    all_courses = Course.query.all()
    return render_template("teacher_dashboard.html", user=user, all_courses=all_courses)


@main.route("/teacher/course/<int:course_id>", methods=["GET", "POST"])
@login_required
def class_detail(course_id):
    course = Course.query.get(course_id)
    students = course.students
    grades = {g.student_id: g for g in Grade.query.filter_by(course_id=course_id).all()}

    if request.method == "POST":
        for student in students:
            grade_val = request.form.get(f"grade_{student.id}")
            if grade_val is not None:
                grade = grades.get(student.id)
                if not grade:
                    grade = Grade(student_id=student.id, course_id=course_id)
                    db.session.add(grade)
                grade.grade = int(grade_val)
        db.session.commit()
        return redirect(url_for("main.class_detail", course_id=course_id))

    return render_template("class_detail.html", course=course, students=students, grades=grades, user=current_user)


# def get_current_user_with_courses():
#     return User.query.options(joinedload(User.courses_enrolled).joinedload(Course.teacher)).get(current_user.id)

@main.route("/teacher/course/<int:course_id>/add_deadline", methods=["GET", "POST"])
@login_required
def add_deadline(course_id):

    """
    /teacher/course/<id>/add_deadline is intuitive and RESTful: modifying a course sub-resource.
    :param course_id:
    :return:
    """
    course = Course.query.get(course_id)

    # Route guards (course.teacher_id != current_user.id) enforce security so only the correct teacher can access it.
    # Verify the teacher owns the course
    if course.teacher_id != current_user.id:
        flash("You do not have permission to add a deadline to this course.")
        return redirect(url_for('main.teacher_dashboard'))

    if request.method == "POST":
        task = request.form.get("task")
        date = request.form.get("date")

        if task and date:
            deadline = Deadline(task=task, date=date, course_id=course.id, teacher_id=current_user.id)
            db.session.add(deadline)
            db.session.commit()
            flash("Deadline added successfully!")
            return redirect(url_for("main.class_detail", course_id=course.id))

    return render_template("add_deadline.html", course=course)
