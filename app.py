from flask import Flask                      # Flask is the main class for creating a Flask app
from flask_login import LoginManager         # Handles user login/session management
from flask_admin import Admin                # Provides an admin dashboard UI for managing models
from flask import current_app                # Gives access to the current app context
from flask_admin.contrib.sqla import ModelView  # Provides default CRUD views for SQLAlchemy models
from wtforms.fields import SelectField       # Allows custom dropdown fields in forms


# Import models and routes defined in your app
from models import *   # Database models
from routes import main                      # app's route blueprint (views)

app = Flask(__name__) # Initialize the Flask application

app.config['SECRET_KEY'] = 'secret-key' # Used for securely signing session cookies
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'  # Using SQLite DB stored in local file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # false to prevent extra memory and CPU overhead

# Init extensions
db.init_app(app)                             # SQLAlchemy with app
login_manager = LoginManager(app)            # Flask-Login
login_manager.login_view = "main.login"      # Redirect to 'main.login' when unauthenticated users try to access login-required pages


# Register blueprint
app.register_blueprint(main)  # Register routes (views) defined in the 'main' Blueprint (from routes.py)


@login_manager.user_loader      # Tells Flask-Login how to load a user from a given user ID
def load_user(user_id):
    with current_app.app_context():   # Make sure we're in the app context (safe to access DB)
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




admin = Admin(app, name='Admin Panel')
# Register the custom Course view to avoid name collision and provide teacher dropdown
admin.add_view(CourseModelView(Course, db.session, name="Course", endpoint="course_admin"))
# Flask-Admin setup
admin.add_view(ModelView(User, db.session))
# admin.add_view(ModelView(Course, db.session))
admin.add_view(ModelView(Grade, db.session))

admin.add_view(DeadlineModelView(Deadline, db.session))


# Create tables on first run
with app.app_context():  # app context to  access db
    db.create_all() # Create tables if they don’t exist

if __name__ == '__main__':
    app.run(debug=True)
