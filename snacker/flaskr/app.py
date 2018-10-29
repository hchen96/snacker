import sys
import urllib

import mongoengine as mg
from flask import Flask, render_template, request, flash, redirect, url_for, make_response
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, current_user, logout_user, login_user
from werkzeug.contrib.fixers import ProxyFix
from mongoengine import *
import json

from forms import RegistrationForm, LoginForm, CreateReviewForm, CreateSnackForm

# from geodata import get_geodata
from schema import Snack, Review, CompanyUser, User, MetricReview
from util import SnackResults, ReviewResults

"""
You need to create a mongo account and let Jayde know your mongo email address to add you to the db system
Then you need to create a password.txt and username.txt each storing the password and username of your mongo account
If the above doesn't work try setting mongo_uri directly to:
mongodb+srv://your_first_name_with_first_letter_capitalized:your_first_name_with_first_letter_capitalized@csc301-v3uno.mongodb.net/test?retryWrites=true
If the above works, it should be a parsing problem try updating Python
If not ask for troubleshoot help in group chat
"""

app = Flask(__name__)

# With these constant strings, we can connect to generic databases
USERNAME_FILE = "username.txt"
PASSWORD_FILE = "password.txt"
DATABASE = "test"
MONGO_SERVER = "csc301-v3uno.mongodb.net"
APP_NAME = "Snacker"

#For snack images
UPLOAD_FOLDER = ""
ALLOWED_FILE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']


try:
    username = open(USERNAME_FILE, 'r').read().strip().replace("\n", "")
    pw = urllib.parse.quote(open(PASSWORD_FILE, 'r').read().strip().replace("\n", ""))
    print("hello")
    mongo_uri = f"mongodb+srv://Jayde:Jayde@csc301-v3uno.mongodb.net/test?retryWrites=true"
    app.config["MONGO_URI"] = mongo_uri
    mongo = mg.connect(host=mongo_uri)
    # This is necessary for user tracking
    app.wsgi_app = ProxyFix(app.wsgi_app, num_proxies=1)
except Exception as inst:
    raise Exception("Error in database connection:", inst)

# TODO: Need to change this to an env variable later
app.config["SECRET_KEY"] = "2a0ca44c88db3d509085f32f2d4ed2e6"
app.config['DEBUG'] = True
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)


@app.route("/index")
def index():
    snacks = Snack.objects
    popular_snacks = snacks.order_by("-review_count")[:5]
    top_snacks = snacks.order_by("-avg_overall_rating")[:5]
    # TODO: Recommend snacks tailored to user
    featured_snacks = top_snacks

    # Use JS Queries later
    # Needs to be a divisor of 12
    interesting_facts = []
    interesting_facts.append(("Snacks", Snack.objects.count()))
    interesting_facts.append(("Reviews", Review.objects.count()))
    interesting_facts.append(("Five stars given", Review.objects(overall_rating=5).count()))

    return render_template('index.html', featured_snacks=featured_snacks, top_snacks=top_snacks,
                           popular_snacks=popular_snacks,
                           interesting_facts=interesting_facts)


@app.route("/about")
def about():
    return render_template('about.html', title='About {APP_NAME}')


# Go to the local url and refresh that page to test
# See below for use cases of different schema objects
@app.route('/')
def hello_world():
    print('This is standard output', file=sys.stdout)
    # Selecting the database we want to work withf
    my_database = mongo[DATABASE]
    for obj in User.objects:
        print(f"   Before Save User: {obj.email} \n", file=sys.stdout)
    for obj in CompanyUser.objects:
        print(f"   Before Save CompanyUser: {obj.email} \n", file=sys.stdout)
    normal_user = User(email="jayde.yue@mail.utoronto.ca", first_name="Jayde", last_name="Yue", password="123123")
    company_user = CompanyUser(email="JaydeYue@jaydeyue.com", first_name="Jayde", last_name="Yue",
                               company_name="The Amazing Jayde Yue Company", password="123123")
    try:
        normal_user.save()
    except Exception as e:
        print("Error \n %s" % e, file=sys.stdout)
    try:
        company_user.save()
    except Exception as e:
        print("Error \n %s" % e, file=sys.stdout)
    # If without error, then both the normal user and company user should display in User collection
    # And only company user should display in CompanyUser collection
    print(f"afaan\n", file=sys.stdout)
    for obj in User.objects:
        print(f"   After Save User: {obj.email} \n", file=sys.stdout)
    for obj in CompanyUser.objects:
        print(f"   After Save CompanyUser: {obj.email} \n", file=sys.stdout)

    # Test Snack
    for obj in Snack.objects:
        print(f"    Before Save Snack: {obj.snack_brand} {obj.snack_name} \n", file=sys.stdout)
    # To test it yourself, create a snack with different name and brand from the exisiting snacks in the db
    snack = Snack(snack_name="Crunchy Cheesy Flavoured", available_at_locations=["Canada"], snack_brand="Cheetos")
    snack.description = "Yummy yum"
    snack.avg_overall_rating = 0
    snack.avg_bitterness = 0
    snack.avg_saltiness = 0
    snack.avg_sourness = 0
    snack.avg_spiciness = 0
    snack.avg_sweetness = 0
    snack.review_count = 0
    try:
        snack.save()
    except Exception as e:
        print("Error \n %s" % e, file=sys.stdout)
    # Display existing snacks in db, your new snack should be here if it has been saved without error
    for obj in Snack.objects:
        print(f"    After Save Snack: {obj.snack_brand} {obj.snack_name} \n", file=sys.stdout)

    # Test Review
    # Display existing reviews in the db
    for obj in Review.objects:
        print(f"    Before Save Review: {obj.user_id} {obj.snack_id} {obj.description}\n", file=sys.stdout)
    review = Review(user_id="5bd148de67afee4602847c74", snack_id="5bd6054687bec22d78d12c59", description="too hot",
                    geolocation="Canada", overall_rating="2")
    try:
        review.save()
        avg_overall_rating = Review.objects.filter(snack_id=review.snack_id).average('overall_rating')
        Snack.objects(id=review.snack_id).update(set__avg_overall_rating=avg_overall_rating)
        review_count = Snack.objects(id=review.snack_id)[0].review_count + 1
        Snack.objects(id=review.snack_id).update(set__review_count=review_count)
    except Exception as e:
        print("Error \n %s" % e, file=sys.stdout)
    for obj in Review.objects:
        print(f"    After Save Review: {obj.user_id} {obj.snack_id} {obj.description}\n", file=sys.stdout)

    # Test MetricReview
    for obj in MetricReview.objects:
        print(f"    Before Save MetricReview: {obj.user_id} {obj.snack_id} {obj.description}\n", file=sys.stdout)
    metric_review = MetricReview(user_id="5bd2897c2c8884ec4714296c", snack_id="5bd6054687bec22d78d12c59",
                                 description="love it!", geolocation="Canada", overall_rating="5", sourness="1",
                                 spiciness="4")
    try:
        metric_review.save()
        avg_overall_rating = Review.objects.filter(snack_id=metric_review.snack_id).average('overall_rating')
        avg_sourness = Review.objects.filter \
            (Q(snack_id=metric_review.snack_id) & Q(sourness__exists=True)).average("sourness")
        avg_spiciness = Review.objects.filter \
            (Q(snack_id=metric_review.snack_id) & Q(spiciness__exists=True)).average("spiciness")
        avg_bitterness = Review.objects.filter \
            (Q(snack_id=metric_review.snack_id) & Q(bitterness__exists=True)).average("bitterness")
        avg_sweetness = Review.objects.filter \
            (Q(snack_id=metric_review.snack_id) & Q(sweetness__exists=True)).average("sweetness")
        avg_saltiness = Review.objects.filter \
            (Q(snack_id=metric_review.snack_id) & Q(saltiness__exists=True)).average("saltiness")
        Snack.objects(id=metric_review.snack_id).update(set__avg_overall_rating=avg_overall_rating)
        Snack.objects(id=metric_review.snack_id).update(set__avg_sourness=avg_sourness)
        Snack.objects(id=metric_review.snack_id).update(set__avg_spiciness=avg_spiciness)
        Snack.objects(id=metric_review.snack_id).update(set__avg_bitterness=avg_bitterness)
        Snack.objects(id=metric_review.snack_id).update(set__avg_sweetness=avg_sweetness)
        Snack.objects(id=metric_review.snack_id).update(set__avg_saltiness=avg_saltiness)
        review_count = Snack.objects(id=metric_review.snack_id)[0].review_count + 1
        Snack.objects(id=metric_review.snack_id).update(set__review_count=review_count)
    except Exception as e:
        print("Error \n %s" % e, file=sys.stdout)
    for obj in MetricReview.objects:
        print(f"    After Save MetricReview: {obj.user_id} {obj.snack_id} {obj.description}\n", file=sys.stdout)
    snacks = Snack.objects
    popular_snacks = snacks.order_by("-review_count")[:5]
    top_snacks = snacks.order_by("-avg_overall_rating")[:5]
    # TODO: Recommend snacks tailored to user
    featured_snacks = top_snacks

    # Use JS Queries later
    # Needs to be a divisor of 12
    interesting_facts = []
    interesting_facts.append(("Snacks", Snack.objects.count()))
    interesting_facts.append(("Reviews", Review.objects.count()))
    interesting_facts.append(("Five stars given", Review.objects(overall_rating=5).count()))

    return render_template('index.html', featured_snacks=featured_snacks, top_snacks=top_snacks,
                           popular_snacks=popular_snacks, interesting_facts=interesting_facts)


@app.route('/register', methods=["GET", "POST"])
def register():
    # IMPORTANT: Encrypt the password for the increased security.
    encrypted_password = lambda password_as_string: bcrypt.generate_password_hash(password_as_string)
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm(request.form)
    if request.method == "POST":
        print(f"dfdsf\n", file=sys.stdout)
        email = request.form['email']
        # Add user to database.
        try:
            new_user = User(email=request.form['email'], first_name=request.form['first_name'],
                            last_name=request.form['last_name'], password=encrypted_password(request.form['password']))
            new_user.save()
        except Exception as e:
            raise Exception(f"Error {e}. \n Couldn't add user {new_user},\n with following registration form: {form}")
        print(f"A new user submitted the registration form: {email}", file=sys.stdout)
        for u in User.objects[:10]:
            print(u)
        user = {
            'email': new_user.email,
            'first_name': new_user.first_name,
            'last_name': new_user.last_name
        }
        response = make_response(json.dumps(user))
        response.status_code = 200
        return response
    return render_template("register.html", title="Register", form=form)


@app.route("/create-review", methods=["GET", "POST"])
@login_required
def create_review():
    # Create a review and insert it into database.

    # check authenticated
    if current_user.is_authenticated:
        print("is_authenticated")

        review_form = CreateReviewForm(request.form)
        # post to db
        if request.method == "POST" and review_form.validate_on_submit():
            user_id = current_user.id
            # should probably check if user_id is in db

            # snack name and brand
            # query for it
            snacks = Snack.objects
            snack_id = snacks.filter(snack_name=request.snack_name).filter(snack_brand=request.snack_brand)

            # geolocation stuff
            # ip_address = request.access_route[0] or request.remote_addr
            # geodata = get_geodata(ip_address)
            # location = "{}, {}".format(geodata.get("city"),
            #                            geodata.get("zipcode"))

            try:
                # user_id comes from current_user
                # snack_id should come from request sent by frontend
                # geolocation is found by request
                new_review = Review(user_id=user_id, snack_id=snack_id,
                                    description=review_form.description.data,
                                    geolocation="Default", overall_rating=review_form.overall_rating.data)
                new_review.save()

            except Exception as e:
                raise Exception(
                    f"Error {e}. \n Couldn't add review {new_review},\n with following review form: {review_form}")

            print(f"A new user submitted the review form: {user_id}", file=sys.stdout)

            for u in Review.objects[:10]:
                print(u)

            return redirect(url_for('index'))
        return render_template("create_review.html", title="Create Review", form=review_form)  # frontend stuff

    else:
        return redirect(url_for('index'))


@app.route("/create-snack", methods=["GET", "POST"])
@login_required
def create_snack():
    # Get snacks from the database.

    if current_user.is_authenticated:
        print("User is authenticated")

        create_snack_form = CreateSnackForm(request.form)

        if request.method == "POST" and create_snack_form.validate_on_submit():
            snack_brand = create_snack_form.snack_brand.data
            snack_name = create_snack_form.snack_name.data

            #Add snack to db
            try:
                new_snack = Snack(snack_name=create_snack_form.snack_name.data,
                                  available_at_locations=create_snack_form.available_at_locations.data,
                                  snack_brand=create_snack_form.snack_brand.data,
                                  description=create_snack_form.description.data,
                                  avg_overall_rating=create_snack_form.avg_overall_rating.data,
                                  avg_sourness=create_snack_form.avg_sourness.data,
                                  avg_spiciness=create_snack_form.avg_spiciness.data,
                                  avg_bitterness=create_snack_form.avg_bitterness.data,
                                  avg_sweetness=create_snack_form.avg_sweetness.data,
                                  avg_saltiness=create_snack_form.avg_saltiness.data)
                new_snack.save()
            except Exception as e:
                raise Exception(f"Error {e}. \n Couldn't add snack {new_snack},\n with following creation form: "
                                f"{create_snack_form}")
            print(f"A new snack submitted the creation form: {snack_brand} => {snack_name}", file=sys.stdout)

            for snack in Snack.objects[:10]:
                print(snack)

            return redirect(url_for('index'))

        #For frontend purposes
        return render_template("create_snack.html", title="Create Snack", form=create_snack_form)
    else:
        #Go back to index if not authenticated
        return redirect(url_for('index'))




""" Routes and methods related to user login and authentication """


@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()


@app.route("/login", methods=["GET", "POST"])
def login():
    # For GET requests, display the login form; for POST, log in the current user by processing the form.
    print(f"LOGGING IN\n", file=sys.stdout)
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm(request.form)

    if request.method == 'POST':
        user = User.objects(email=request.form['email']).first()
        print(f"user is {user}\n", file=sys.stdout)
        if user is None or not user.check_password(bcrypt, request.form['password']):
            flash("Invalid username or password")
            return redirect(url_for('login'))
        login_user(user, remember=True)
        user = {
            'email': current_user.email,
            'first_name': current_user.first_name,
            'last_name': current_user.last_name
        }
        response = make_response(json.dumps(user))
        response.status_code = 200
        return response
    return render_template('login.html', title='Sign In', form=form)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for('index'))


# Finished and tested
@app.route("/snack_reviews/<string:filters>", methods=['GET'])
def find_reviews_for_snack(filters):
    """
    Find all reviews given filter
    For overall rating, and the metrics, all reviews with greater or equal to the given value will be returned
    Results currently ordered by descending overall rating
    /snack_reviews/snack_id=abc+overall_rating=3...
    """
    all_filters = filters.split("+")
    print(f"{all_filters}\n", file=sys.stdout)
    queryset = Review.objects
    # all reviews will be returned if nothing specified
    if "=" in filters:
        for individual_filter in all_filters:
            this_filter = individual_filter.split("=")
            if this_filter[0] == "user_id":
                queryset = queryset.filter(user_id=this_filter[1])
            elif this_filter[0] == "snack_id":
                queryset = queryset.filter(snack_id=this_filter[1])
            elif this_filter[0] == "overall_rating":
                queryset = queryset.filter(overall_rating__gte=this_filter[1])
            elif this_filter[0] == "geolocation":
                queryset = queryset.filter(geolocation=this_filter[1])
            elif this_filter[0] == "sourness":
                queryset = queryset.filter(sourness__gte=this_filter[1])
            elif this_filter[0] == "spiciness":
                queryset = queryset.filter(spiciness__gte=this_filter[1])
            elif this_filter[0] == "bitterness":
                queryset = queryset.filter(bitterness__gte=this_filter[1])
            elif this_filter[0] == "sweetness":
                queryset = queryset.filter(sweetness__gte=this_filter[1])
            elif this_filter[0] == "saltiness":
                queryset = queryset.filter(saltiness__gte=this_filter[1])
    queryset = queryset.order_by("-overall_rating")
    print(f"snack_reviews: {queryset}", file=sys.stdout)
    display = ReviewResults(queryset)
    display.border = True
    # Return results in a table, the metrics such as sourness are not displayed because if they are null, they give
    #   the current simple front end table an error, but it is there for use
    return render_template('reviews_for_snack.html', table=display)


# Finished and tested
@app.route("/find_snacks/<string:filters>", methods=['GET'])
def find_snack_by_filter(filters):
    """
    Find all snacks given filter
    Only support searching for one location at a time now (i.e. can't find snacks both in USA and Canada)
    For is verfied, false for false and true for true
    Results currently ordered by snack name
    For snack name, it will return all snacks that contain the string given by snack_name instead of only returning the
        snacks with exactly the same name
    /find_snacks/snack_name=abc+available_at_locations=a+...
    /find_snacks/all if we want to get all snacks
    """
    all_filters = filters.split("+")
    print(f"{all_filters}\n", file=sys.stdout)
    queryset = Snack.objects

    # the search string should be all if we want to get all snacks, but we can type anything that doesn't include = to
    #   get the same results
    if "=" in filters:
        for individual_filter in all_filters:
            this_filter = individual_filter.split("=")
            if this_filter[0] == "snack_name":
                # Change to contain so that snacks with similar name to inputted name will be returned too
                if this_filter[1] != "":
                    queryset = queryset.filter(snack_name__contains=this_filter[1])
            elif this_filter[0] == "available_at_locations":
                # Note for this, say if they enter n, they will still return snacks in Canada because their contains
                #   is based on string containment. If order to solve this, we can let force users to select countries
                #   instead of typing countries
                if this_filter[1] != "all":
                    queryset = queryset.filter(available_at_locations__contains=this_filter[1])
            elif this_filter[0] == "snack_brand":
                if this_filter[1] != "":
                    queryset = queryset.filter(snack_brand=this_filter[1])
            elif this_filter[0] == "snack_company_name":
                queryset = queryset.filter(snack_company_name=this_filter[1])
            elif this_filter[0] == "is_verified":
                if this_filter[1] == "false":
                    queryset = queryset.filter(is_verified=False)
                else:
                    queryset = queryset.filter(is_verified=True)
            elif this_filter[0] == "category":
                queryset = queryset.filter(category=this_filter[1])
    queryset = queryset.order_by("snack_name")
    print(f"snack_reviews: {queryset}", file=sys.stdout)
    display = SnackResults(queryset)
    display.border = True
    # Return the same template as for the review, since it only needs to display a table.
    return render_template('reviews_for_snack.html', table=display)


if __name__ == '__main__':
    app.run()
