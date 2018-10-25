from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from schema import User

class RegistrationForm(FlaskForm):
    first_name = StringField("First Name", [DataRequired(), Length(min=2, max=100)])
    last_name = StringField("Last Name", [DataRequired(), Length(min=2, max=100)])
    email = StringField("Email Address", [
        Email("Invalid email provided"),
        Length(min=6, max=100),
        DataRequired("Please provide an email")
    ])
    is_company = BooleanField("Are you a company or distributor?")
    password = PasswordField("New Password (maximum length is 50)", [
        DataRequired(),
        Length(max=50),
        EqualTo("confirm", message="Passwords don't match")
    ])
    confirm = PasswordField("Repeat Password", [DataRequired()])
    accept_tos = BooleanField("I accept the Terms of Service and Privacy Notice", [DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_email(self, field):
        """Prevents multiple users with the same email"""
        user = User.objects(email=field.data).first();
        if user is not None:
            raise ValidationError("This email is already registered, please use another")


class LoginForm(FlaskForm):
    email = StringField("Email Address", [
        Email("Invalid email provided"),
        Length(min=6, max=100),
        DataRequired("Please use your email to login")
    ])
    password = PasswordField("New Password", [DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')



