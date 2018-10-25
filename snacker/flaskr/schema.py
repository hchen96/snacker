from mongoengine import *
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import generate_password_hash

# An user of our app
# An unique ID should be automatically created, should be able to refer to it as user._id
# Date of registration is not needed since with automatic _id, it comes with automatic timestamp: getTimestamp()
class User(UserMixin, Document):
    email = EmailField(required=True, unique=True)
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    # You can mess with img size here
    avatar_file = ImageField()
    # If the email has been verified, even for regular users we need to verify email
    is_verified = BooleanField(required=True, default=False)
    _password = StringField(max_length=255, required=True, db_field='password')
    wish_list = ListField(IntField())
    authenticated = BooleanField(default=False)
    meta = {'allow_inheritance': True}

    def __init__(self, email=None, first_name=None, last_name=None, password=None, *args, **kwargs):
        """
        This is necessary for automatically setting the password for
        the User, by direct access. This uses a >setter< for password attribute.

        With this, it's possible to use:
            user = User(email='1@1.com', password='12345')
        and the password will be automatically encrypted
        """

        super(Document, self).__init__(*args, **kwargs)
        if 'password' in kwargs:
            self._password = generate_password_hash(kwargs['password'])
    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def is_authenticated(self):
        return self.authenticated

    def get_id(self):
        return self._id

    def __str__(self):
        return f"[\n\tEmail: {self.email}\n\tfirst_name: {self.first_name}\n\tpw: {self.password}\n]"

    def __repr__(self):
        return f"[\n\tEmail: {self.email}\n\tfirst_name: {self.first_name}\n\tpw: {self.password}\n]"


# Every CompanyUser will be user as well, we can also directly get all CompanyUsers
class CompanyUser(User):
    company_name = StringField(required=True, unique=True)
    company_snackbrands = ListField(StringField(max_length=100))


# A snack
# An unique ID should be automatically created, should be able to refer to it as snack.id
class Snack(Document):
    snack_name = StringField(required=True, unique_with='snack_brand')
    # Countries where the snacks have been reviewed
    available_at_locations = ListField(StringField(), required=True)
    snack_brand = StringField(required=True)
    snack_company_name = StringField()
    # Can mess with img size here
    photo_files = ListField(ImageField())
    description = StringField()
    is_verified = BooleanField(required=True, default=False)
    category = StringField()


# A review of a snack
# An unique ID should be automatically created, should be able to refer to it as review.id
# Timestamp is not needed since with automatic id, it comes with automatic timestamp: getTimestamp()
class Review(Document):
    # ID of user who wrote the review
    user_id = ObjectIdField(required=True)
    # ID of snack that the review is being written about, unique because users shouldn't review twice
    snack_id = ObjectIdField(required=True)
    description = StringField()
    overall_rating = IntField(required=True)
    # Name of country
    geolocation = StringField(required=True)
    meta = {'allow_inheritance': True}


# Every MetricReview will be review as well, we can also directly get all metric reviews
class MetricReview(Review):
    sourness = IntField()
    spiciness = IntField()
    bitterness = IntField()
    sweetness = IntField()
    saltiness = IntField()
