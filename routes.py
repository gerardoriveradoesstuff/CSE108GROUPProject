# flask imports
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from forms import LoginForm, RegisterForm

# security imports
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

# db/model imports
from models import db, User, Course, Grade, Deadline
from models import Transaction, Category, Report
from sqlalchemy import func
from sqlalchemy.orm import joinedload

# MISC imports
from datetime import datetime, UTC

main = Blueprint('main', __name__)


@main.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists")
            return render_template("template-register.html", form=form)

        hashed_password = generate_password_hash(form.password.data)

        new_user = User(
            username=form.username.data,
            password=hashed_password,   # set the hashed password here
            role=form.role.data,
            email = form.email.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for("main.login"))

    return render_template("template-register.html", form=form)


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
    return render_template("template-login.html", form=form)

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
    # return render_template("template-student-dashboard.html", user=current_user, all_courses=all_courses)
    # re-fetch the user with all relationships eagerly loaded

    user = User.query.options(joinedload(User.courses_enrolled).joinedload(Course.teacher)).get(current_user.id)
    return render_template("template-student-dashboard.html", user=user)

@main.route("/profile" , methods=["GET", "POST"])
@login_required
def profile():
    user = User.query.options(joinedload(User.courses_enrolled).joinedload(Course.teacher)).get(current_user.id)
    if request.method == 'POST':
        # Update user profile
        user.bio = request.form.get('bio')
        user.linkedin_url = request.form.get('linkedin_url')
        user.pronunciation = request.form.get('pronunciation')

        try:
            db.session.commit()
            flash("Profile updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating your profile.", "danger")

        return redirect(url_for('main.profile'))
        # Eagerly load user with enrolled courses

    return render_template('template-profile.html', user=user)

@main.route("/my_courses", methods=["GET"])
@login_required
def my_courses():
    all_courses = Course.query.all()
    # Map course_id to grade for current student
    user = User.query.options(joinedload(User.courses_enrolled).joinedload(Course.teacher)).get(current_user.id)
    grade_map = {
        g.course_id: g.grade for g in Grade.query.filter_by(student_id=user.id).all()
    }
    return render_template("template-my-courses.html", user=user, all_courses=all_courses, grade_map=grade_map)


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

    return redirect(url_for("main.my_courses"))

@main.route("/student/drop/<int:course_id>", methods=["POST"])
@login_required
def drop_course(course_id):
    user = User.query.options(joinedload(User.courses_enrolled)).get(current_user.id)
    course = Course.query.get(course_id)
    if course and course in user.courses_enrolled:
        user.courses_enrolled.remove(course)
        db.session.commit()
    return redirect(url_for("main.my_courses"))

@main.route("/teacher")
@login_required
def teacher_dashboard():
    user = User.query.options(joinedload(User.courses_enrolled).joinedload(Course.teacher)).get(current_user.id)
    all_courses = Course.query.all()
    return render_template("template-teacher-dashboard.html", user=user, all_courses=all_courses)


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
                grade.grade = str(grade_val)
        db.session.commit()
        return redirect(url_for("main.class_detail", course_id=course_id))

    return render_template("template-class-detail.html", course=course, students=students, grades=grades, user=current_user)


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
        assignment = request.form.get("assignment")
        due_date = request.form.get("due-date")

        if assignment and due_date:
            deadline = Deadline(assignment=assignment, due_date=due_date, course_id=course.id, user_id=current_user.id)
            db.session.add(deadline)
            db.session.commit()
            flash("Deadline added successfully!")
            return redirect(url_for("main.class_detail", course_id=course.id))

    return render_template("template-add-deadline.html", course=course)


@main.route('/finance')
def finance_dashboard():
    return render_template('template-finance.html', user=current_user)

# @main.route('/add-user', methods=['POST'])
# def add_user():
#     """
#     (1) Query: Insert a new user into the User table.
#     SQL Equivalent:
#     INSERT INTO User (name, email) VALUES (:name, :email);
#     """
#     data = request.json
#     name = data.get('name')
#     email = data.get('email')
#
#     if not name or not email:
#         return jsonify({'error': 'Name and email are required'}), 400
#
#     try:
#         user = User(name=name, email=email)
#         db.session.add(user)  # Add the user to the session
#         db.session.commit()  # Commit the session to insert the user
#         return jsonify({'message': 'User created', 'user_id': user.user_id}), 201
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# @main.route('/fetch-recent-users', methods=['GET'])
# def fetch_recent_users():
#     """
#     (2) Query: Fetch all users.
#     SQL Equivalent:
#     SELECT * FROM User;
#     """
#     try:
#         recent_users = User.query.order_by(User.user_id.desc()).limit(5).all()
#         # users = User.query.all() # use this to query all the users
#         print(f"Fetched users: {recent_users}")  # Debugging
#         result = [{'user_id': u.user_id, 'name': u.name, 'email': u.email} for u in recent_users]
#         return jsonify(result), 200
#     except Exception as e:
#         print(f"Error fetching users: {e}")  # Debugging
#         return jsonify({'error': str(e)}), 500

@main.route('/add-transaction', methods=['POST'])
def add_transaction():
    """
    (3) Query: Adds a new transaction to the Transactions table.
    SQL Equivalent:
    INSERT INTO Transactions (user_id, date, income, expense, category_id, description)
    VALUES (<user_id>, <date>, <income>, <expense>, <category_id>, <description>);
    """
    try:
        data = request.json
        user_id = int(data.get('user_id'))
        category_id = int(data.get('category_id'))
        income = float(data.get('income', 0))
        expense = float(data.get('expense', 0))
        date_str = data.get('date', datetime.now(UTC).strftime('%Y-%m-%d'))
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        description = data.get('description', '')

        # Validate user and category
        user = db.session.get(User, user_id)
        category = db.session.get(Category, category_id)
        if not user:
            return jsonify({'error': f'User with ID {user_id} does not exist.'}), 400
        if not category:
            return jsonify({'error': f'Category with ID {category_id} does not exist.'}), 400

        # Validate that only one field is filled
        if (income == 0 and expense == 0) or (income > 0 and expense > 0):
            return jsonify({'error': 'Please provide either income or expense, but not both.'}), 400

        if not data:
            return jsonify({'error': 'Missing JSON payload'}), 400

        if user_id is None or category_id is None:
            return jsonify({'error': 'Missing user_id or category_id'}), 400


        # Create a new transaction
        transaction = Transaction(
            user_id=user_id,
            category_id=category_id,
            income=income,
            expense=expense,
            description=description,
            date=date
        )

        db.session.add(transaction)
        db.session.commit()

        return jsonify({'message': 'Transaction added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/get-transaction/<int:transaction_id>', methods=['GET'])
@login_required
def get_transaction(transaction_id):
    """
    (4) Query: Fetch a transaction by ID.
    SQL Equivalent:
    SELECT * FROM Transactions WHERE transaction_id = :transaction_id;
    """
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404

    result = jsonify({
        'transaction_id': transaction.transaction_id,
        'category_id': transaction.category_id,
        'income': transaction.income,
        'expense': transaction.expense,
        'description': transaction.description,
        'date': transaction.date.strftime('%Y-%m-%d'),
    })
    return result, 200


@main.route('/update-transaction/<int:transaction_id>', methods=['PUT'])
@login_required
def update_transaction(transaction_id):
    """
    (5) Query: Update a transaction by ID.
    SQL Equivalent:
    UPDATE Transactions SET income=:income, expense=:expense, category_id=:category_id,
    description=:description, date=:date WHERE transaction_id = :transaction_id;
    """
    try:
        data = request.json
        income = float(data.get('income', 0))
        expense = float(data.get('expense', 0))
        category_id = int(data.get('category_id')) if data.get('category_id') else None
        description = data.get('description', '')
        date = data.get('date', datetime.utcnow().strftime('%Y-%m-%d'))

        if not transaction_id:
            return jsonify({'error': 'Transaction ID is required.'}), 400

        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return jsonify({'error': 'Transaction not found.'}), 404

        # Update fields
        transaction.income = income
        transaction.expense = expense
        transaction.category_id = category_id
        transaction.description = description
        transaction.date = datetime.strptime(date, '%Y-%m-%d').date()

        db.session.commit()

        return jsonify({'message': 'Transaction updated successfully.'}), 200
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@main.route('/delete-transaction/<int:transaction_id>', methods=['DELETE'])
@login_required
def delete_transaction(transaction_id):
    """
    (6) Query: Delete a transaction by ID.
    SQL Equivalent:
    DELETE FROM Transactions WHERE transaction_id = :transaction_id;
    """
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404

    db.session.delete(transaction)
    db.session.commit()
    return jsonify({'message': 'Transaction deleted successfully'}), 200

@main.route('/fetch-transactions', methods=['GET', 'POST'])
@login_required
def fetch_transactions():
    """
    (7) Query:
    Fetch transactions for a user in a specific year and month.
    SQL Equivalent (POST):
    SELECT * FROM Transactions
    WHERE user_id = :user_id AND strftime('%Y', date) = :year AND strftime('%m', date) = :month;

    SQL Equivalent (GET):
    SELECT * FROM Transactions;
    """
    try:
        if request.method == 'POST':
            # POST: Filter transactions based on user_id, year, and month
            data = request.json
            user_id = data.get('user_id')
            year = data.get('year')
            month = data.get('month')

            if not user_id or not year or not month:
                return jsonify({'error': 'User ID, year, and month are required'}), 400

            transactions = Transaction.query.filter(
                Transaction.user_id == user_id,
                db.extract('year', Transaction.date) == year,
                db.extract('month', Transaction.date) == month
            ).all()

        else:
            # GET: Fetch all transactions
            transactions = Transaction.query.all()

        # Format the response
        result = [{
            'transaction_id': t.transaction_id,
            'date': t.date.strftime('%Y-%m-%d'),
            'income': t.income if t.income is not None else 0.0,
            'expense': t.expense if t.expense is not None else 0.0,
            'user_id': t.user_id,
            'category': t.category.name if t.category else "N/A",
            'description': t.description if t.description else "N/A"
        } for t in transactions]

        print("Fetched Transactions:", result)  # Debugging
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/add-category', methods=['POST'])
def add_category():
    """
    (8) Query: Adds a new category to the Category table.
    SQL Equivalent:
    INSERT INTO Category (name) VALUES (<category_name>);
    """
    data = request.json
    category_name = data.get('name')

    if not category_name:
        return jsonify({'error': 'Category name is required'}), 400

    try:
        # Check if the category already exists
        existing_category = Category.query.filter_by(name=category_name).first()
        if existing_category:
            return jsonify({'error': 'Category already exists'}), 400

        # Add the new category
        category = Category(name=category_name)
        db.session.add(category)
        db.session.commit()
        print(f"Added category: {category.name}")  # Debugging: Logs the category name
        return jsonify({
            'message': 'Category added successfully',
            'category_id': category.category_id,
            'name': category.name
        }), 201
    except Exception as e:
        print(f"Error adding category: {e}")  # Debugging: Logs any error encountered
        return jsonify({'error': str(e)}), 500

@main.route('/fetch-categories', methods=['GET'])
def fetch_categories():
    """
    (9) Query: Fetch all categories.
    SQL Equivalent:
    SELECT * FROM Category;
    """
    try:
        categories = Category.query.all()
        result = [{'category_id': c.category_id, 'name': c.name} for c in categories]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/generate-report', methods=['POST'])
def generate_report():
    """
    Query:
    1. Calculate total income, total expense, and balance for a user in a specific month and year.
    2. Fetch the smallest and largest transactions (income/expense).
    3. Calculate the average income and average expense.
    """
    data = request.json
    user_id = data.get('user_id')
    year = data.get('year')
    month = data.get('month')

    if not user_id or not year or not month:
        return jsonify({'error': 'User ID, year, and month are required'}), 400

    try:
        # Query to calculate total income and expense
        total_income = db.session.query(func.sum(Transaction.income)).filter(
            Transaction.user_id == user_id,
            func.extract('year', Transaction.date) == year,
            func.extract('month', Transaction.date) == month,
            Transaction.income > 0
        ).scalar() or 0.0

        total_expense = db.session.query(func.sum(Transaction.expense)).filter(
            Transaction.user_id == user_id,
            func.extract('year', Transaction.date) == year,
            func.extract('month', Transaction.date) == month,
            Transaction.expense > 0
        ).scalar() or 0.0

        # Calculate balance
        balance = total_income - total_expense

        # Query to calculate average income and expense
        average_income = db.session.query(func.avg(Transaction.income)).filter(
            Transaction.user_id == user_id,
            func.extract('year', Transaction.date) == year,
            func.extract('month', Transaction.date) == month,
            Transaction.income > 0
        ).scalar() or 0.0

        average_expense = db.session.query(func.avg(Transaction.expense)).filter(
            Transaction.user_id == user_id,
            func.extract('year', Transaction.date) == year,
            func.extract('month', Transaction.date) == month,
            Transaction.expense > 0
        ).scalar() or 0.0

        # Query to fetch the largest income and expense transactions
        largest_income = db.session.query(Transaction).filter(
            Transaction.user_id == user_id,
            func.extract('year', Transaction.date) == year,
            func.extract('month', Transaction.date) == month,
            Transaction.income > 0
        ).order_by(Transaction.income.desc()).first()

        smallest_expense = db.session.query(Transaction).filter(
            Transaction.user_id == user_id,
            func.extract('year', Transaction.date) == year,
            func.extract('month', Transaction.date) == month,
            Transaction.expense > 0
        ).order_by(Transaction.expense.asc()).first()

        # Fetch all transactions
        transactions = Transaction.query.filter(
            Transaction.user_id == user_id,
            func.extract('year', Transaction.date) == year,
            func.extract('month', Transaction.date) == month
        ).all()

        # Format results
        result = {
            'user_id': user_id,
            'year': year,
            'month': month,
            'total_income': round(total_income, 2),
            'total_expense': round(total_expense, 2),
            'balance': round(balance, 2),
            'average_income': round(average_income, 2),
            'average_expense': round(average_expense, 2),
            'largest_income': {
                'transaction_id': largest_income.transaction_id if largest_income else None,
                'amount': largest_income.income if largest_income else 0.0,
                'date': largest_income.date.strftime('%Y-%m-%d') if largest_income else "N/A",
                'description': largest_income.description if largest_income else "N/A"
            },
            'smallest_expense': {
                'transaction_id': smallest_expense.transaction_id if smallest_expense else None,
                'amount': smallest_expense.expense if smallest_expense else 0.0,
                'date': smallest_expense.date.strftime('%Y-%m-%d') if smallest_expense else "N/A",
                'description': smallest_expense.description if smallest_expense else "N/A"
            },
            'transactions': [{
                'transaction_id': t.transaction_id,
                'date': t.date.strftime('%Y-%m-%d'),
                'income': t.income or 0.0,
                'expense': t.expense or 0.0,
                'category': t.category.name if t.category else "N/A",
                'description': t.description or "N/A"
            } for t in transactions]
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
