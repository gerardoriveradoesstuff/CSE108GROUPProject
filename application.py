from flask import Flask, jsonify                     # Flask is the main class for creating a Flask application
from flask_login import LoginManager         # Handles user login/session management
from flask_admin import Admin                # Provides an admin dashboard UI for managing models
from flask import current_app                # Gives access to the current application context
from flask_admin.contrib.sqla import ModelView  # Provides default CRUD views for SQLAlchemy models
from wtforms import SelectField
from forms import UserAdminForm
from dotenv import load_dotenv
from flask_migrate import Migrate


# Import models and routes defined in your application
from models import *   # Database models
from routes import main, teacher                      # application's route blueprint (views)

load_dotenv()  # Load .env file
application = Flask(__name__) # Initialize the Flask application

application.config['SECRET_KEY'] = 'secret-key' # Used for securely signing session cookies
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'  # Using SQLite DB stored in local file
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # false to prevent extra memory and CPU overhead

# Init extensions
db.init_app(application)                             # SQLAlchemy with application
migrate = Migrate(application, db)

login_manager = LoginManager(application)            # Flask-Login
login_manager.login_view = "main.login"      # Redirect to 'main.login' when unauthenticated users try to access login-required pages


# Register blueprint
application.register_blueprint(main)  # Register routes (views) defined in the 'main' Blueprint (from routes.py)
application.register_blueprint(teacher) 

# @main.route('/api/news')
# def get_news():
#     api_key = os.getenv("NEWS_API_KEY")
#     if not api_key:
#         return jsonify({"error": "API key missing"}), 500
#
#     url = "https://newsapi.org/v2/everything"
#     params = {
#         "q": "computer science statistics",
#         "language": "en",
#         "sortBy": "publishedAt",
#         "pageSize": 5,
#         "apiKey": api_key
#     }
#
#     try:
#         response = requests.get(url, params=params)
#         return jsonify(response.json())
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@login_manager.user_loader      # Tells Flask-Login how to load a user from a given user ID
def load_user(user_id):
    with current_app.app_context():   # Make sure we're in the application context (safe to access DB)
        return db.session.get(User, int(user_id))  # Use SQLAlchemy 2.x style to retrieve a user by primary key


# Flask-Admin customization
class CourseModelView(ModelView):  # Custom admin view for the Flask-Admin
    form_overrides = dict(teacher_id=SelectField) # Override the default field with a dropdown to select teacher when creating class
    form_args = {'teacher_id': {'label': 'Teacher'}} # Label for the dropdown
    form_columns = ['name', 'time', 'capacity', 'teacher_id']  #  important: Specify visible/editable form fields

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.teacher_id.choices = [
            (t.id, t.username) for t in User.query.filter_by(role='teacher').all()
        ]
        return form

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        form.teacher_id.choices = [
            (t.id, t.username) for t in User.query.filter_by(role='teacher').all()
        ]
        return form


class DeadlineModelView(ModelView):
    form_columns = ['assignment', 'due_date', 'course_id', 'user_id']
    form_overrides = dict(course_id=SelectField, user_id=SelectField)
    form_args = {
        'course_id': {'label': 'Course'},
        'user_id': {'label': 'Teacher'}
    }

    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.course_id.choices = [(c.id, c.name) for c in Course.query.all()]
        form.user_id.choices = [(u.id, u.username) for u in User.query.filter_by(role='teacher')]
        return form

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        form.course_id.choices = [(c.id, c.name) for c in Course.query.all()]
        form.user_id.choices = [(u.id, u.username) for u in User.query.filter_by(role='teacher')]
        return form


class UserModelView(ModelView):
    form = UserAdminForm  # use the custom form
    form_columns = ['username', 'email', 'password', 'role']
    column_exclude_list = ['password']

    def on_model_change(self, form, model, is_created):
        from werkzeug.security import generate_password_hash
        if is_created or not check_password_hash(model.password, form.password.data):
            model.password = generate_password_hash(form.password.data)

admin = Admin(application, name='Admin Panel')
# Register the custom Course view to avoid name collision and provide teacher dropdown
admin.add_view(CourseModelView(Course, db.session, name="Course", endpoint="course_admin"))
# Flask-Admin setup
admin.add_view(UserModelView(User, db.session))
# admin.add_view(ModelView(Course, db.session))
admin.add_view(ModelView(Grade, db.session))

admin.add_view(DeadlineModelView(Deadline, db.session))


# Create tables on first run

with application.app_context():  # application context to  access db
    db.create_all() # Create tables if they don’t exist
    # IF USING FLASK MIGRATE THIS IS NOT NEEDED, BUT ALSO WON'T BREAK THINGS
    # BEST TO RELY ON MIGRATE IF USING MIGRATE. MIGRATE USE MIGRATE

if __name__ == '__main__':
    application.run(debug=True)