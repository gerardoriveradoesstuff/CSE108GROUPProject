from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")

class GradeForm(FlaskForm):
    grade = IntegerField("Grade", validators=[DataRequired()])
    submit = SubmitField("Update")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    role = SelectField("Role", choices=[('student', 'Student'), ('teacher', 'Teacher')], validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Register")

class UserAdminForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    role = SelectField("Role", choices=[("student", "Student"), ("teacher", "Teacher")], validators=[DataRequired()])

class ForumPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])


class TeacherProfileForm(FlaskForm):
    office_location = StringField('Office Location', validators=[Length(max=100)])
    office_hours = StringField('Office Hours', validators=[Length(max=100)])
    department = SelectField('Department', choices=[
        ('', 'Select Department'),
        ('computer_science', 'Computer Science'),
        ('mathematics', 'Mathematics'),
        ('physics', 'Physics'),
        ('engineering', 'Engineering'),
        ('business', 'Business')
    ])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    submit = SubmitField('Save Profile')