from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError, NumberRange
from schema import User
from mongoengine import *
import pycountry


class RegistrationForm(FlaskForm):
    first_name = StringField("First Name", [DataRequired(), Length(min=2, max=100)])
    last_name = StringField("Last Name", [DataRequired(), Length(min=2, max=100)])
    email = StringField("Email Address", [
        Email("Invalid email address provided"),
        Length(min=6, max=100),
        DataRequired("Please provide an email address")
    ])
    is_company = BooleanField("Are you a company or a distributor?")
    password = PasswordField("New Password (maximum length is 50)", [
        DataRequired(),
        Length(max=50),
        EqualTo("confirm", message="Passwords don't match")
    ])
    confirm = PasswordField("Repeat Password", [DataRequired()])
    accept_tos = BooleanField("I accept the Terms of Service and Privacy Notice", [DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_email(self, field):
        """Prevent multiple users from having the same email address"""
        user = User.objects(email=field.data).first()
        if user is not None:
            raise ValidationError("This email is already registered, please use another email address")


class LoginForm(FlaskForm):
    email = StringField("Email Address", [
        Email("Invalid email address provided"),
        Length(min=6, max=100),
        DataRequired("Please use your email address to login")
    ])
    password = PasswordField("Password", [DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class CreateReviewForm(FlaskForm):

    # user_id = ObjectIdField("User Id", [DataRequired(), ])
    # snack_id = ObjectIdField("Snack Id", [DataRequired(), ])
    # geolocation = ("First Name", [DataRequired(), Length(min=2, max=100)])
    #above comes from backend

    description = StringField("Review Description", [Length(min=2, max=255)])
    overall_rating = IntField("Overall Rating", [DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Submit Review')

class CreateSnackForm(FlaskForm):

    snack_name = StringField("Snack Name", [DataRequired(), Length(min=2, max=50)])

    #SelectField for a selection of as many countries
    def __init__(self, *args, **kwargs):
        super(CountrySelectField, self).__init__(*args, **kwargs)
        self.choices = ["No Country Selected"]
        for country in pycountry.countries:
            self.choices.append(country.name)

    snack_brand = StringField("Snack Brand", [DataRequired(), Length(min=2, max=50)])
    # photo_file = FileField("Upload Photo", [FileAllowed(photo_file, u'Image only!'), FileRequired(u'File was empty!')])
    description = StringField("Snack Description", [Length(min=2, max=255)])
    avg_overall_rating = IntField("Overall Rating", [DataRequired(), NumberRange(min=1, max=5)])
    avg_sourness = IntField("Sourness Rating", [DataRequired(), NumberRange(min=1, max=5)])
    avg_spiciness = IntField("Spiciness Rating", [DataRequired(), NumberRange(min=1, max=5)])
    avg_bitterness = IntField("Bitterness Rating", [DataRequired(), NumberRange(min=1, max=5)])
    avg_sweetness = IntField("Sweetness Rating", [DataRequired(), NumberRange(min=1, max=5)])
    avg_saltiness = IntField("Saltiness Rating", [DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Submit Snack')


