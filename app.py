from flask import Flask
from flask_login import LoginManager
from flask_admin import Admin
from flask import current_app
from flask_admin.contrib.sqla import ModelView
from wtforms.fields import SelectField

from models import db, User, Course, Grade
from routes import main

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "main.login"

# Register blueprint
app.register_blueprint(main)


@login_manager.user_loader
def load_user(user_id):
    with current_app.app_context():
        return db.session.get(User, int(user_id))

# Flask-Admin customization
class CourseModelView(ModelView):
    form_overrides = dict(teacher_id=SelectField)
    form_args = {'teacher_id': {'label': 'Teacher'}}
    form_columns = ['name', 'time', 'capacity', 'teacher_id']  # 👈 important

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



admin = Admin(app, name='Admin Panel')
admin.add_view(CourseModelView(Course, db.session, name="Course", endpoint="course_admin"))
# Flask-Admin setup
admin.add_view(ModelView(User, db.session))
# admin.add_view(ModelView(Course, db.session))
admin.add_view(ModelView(Grade, db.session))




# Create tables on first run
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
