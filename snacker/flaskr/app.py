import json
import mimetypes
import sys
import urllib

from flask import Flask, render_template, request, flash, redirect, url_for, make_response, Response
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, current_user, logout_user, login_user
from mongoengine import connect
from mongoengine.queryset.visitor import Q
from werkzeug.contrib.fixers import ProxyFix

from forms import RegistrationForm, LoginForm, CreateReviewForm, CreateSnackForm
from schema import Snack, Review, CompanyUser, User, MetricReview

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

# For snack images
UPLOAD_FOLDER = ""
ALLOWED_FILE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']

try:
    username = open(USERNAME_FILE, 'r').read().strip().replace("\n", "")
    pw = urllib.parse.quote(open(PASSWORD_FILE, 'r').read().strip().replace("\n", ""))
    print("hello")
    mongo_uri = f"mongodb+srv://Jayde:Jayde@csc301-v3uno.mongodb.net/test?retryWrites=true"
    # mongo_uri = "mongodb://localhost:27017/"
    app.config["MONGO_URI"] = mongo_uri
    mongo = connect(host=mongo_uri)
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
app.url_map.strict_slashes = False


@app.route('/render-img/<string:snack_id>')
def serve_img(snack_id):
    """ Given a snack id, get the image and render it
        Example in file display_snack.html"""
    placeholder = "static/images/CrunchyCheesyFlavouredCheetos.jpg"
    get_mimetype = lambda filename: mimetypes.MimeTypes().guess_type(filename)[0]
    sample_snack = Snack.objects(id=snack_id)[0]
    if sample_snack.photo_files == []:
        return Response(open(placeholder, "rb").read(), mimetype=get_mimetype(placeholder))
    photo = sample_snack.photo_files[0].img
    # resp=Response(photo.read(), mimetype=mimetype)
    # Returning the thumbnail for now
    resp = Response(photo.thumbnail.read(), mimetype=get_mimetype(photo.filename))
    return resp


@app.route("/index")
def index():
    if current_user.is_authenticated:
        print("ok")
    max_show = 5  # Maximum of snacks to show
    snacks = Snack.objects
    popular_snacks = snacks.order_by("-review_count")[:max_show]
    top_snacks = snacks.order_by("-avg_overall_rating")
    featured_snacks = []
    # Getting snacks that have some image to display
    for snack in top_snacks:
        if snack.photo_files:
            featured_snacks.append(snack)
            if len(featured_snacks) == max_show:
                break
    # TODO: Recommend snacks tailored to user
    # featured_snacks = top_snacks

    # Use JS Queries later
    # Needs to be a divisor of 12
    interesting_facts = []
    interesting_facts.append(("Snacks", snacks.count()))
    interesting_facts.append(("Reviews", Review.objects.count()))
    interesting_facts.append(("Five stars given", Review.objects(overall_rating=5).count()))

    context_dict = {"featured_snacks": featured_snacks,
                    "top_snacks": snacks.order_by("-avg_overall_rating")[:5],
                    "popular_snacks": snacks.order_by("-review_count")[:5],
                    "interesting_facts": interesting_facts,
                    "user": current_user}
    return render_template('index.html', **context_dict)


@app.route("/about")
def about():
    context_dict = {"title": 'About {APP_NAME}',
                    "user": current_user}
    return render_template('about.html', **context_dict)


@app.route("/contact")
def contact():
    context_dict = {"title": 'Contact Us',
                    "user": current_user}
    return render_template('contact.html', **context_dict)


# Go to the local url and refresh that page to test
# See below for use cases of different schema objects
@app.route('/')
def hello_world():
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

    context_dict = {"featured_snacks": snacks.order_by("-avg_overall_rating")[:5],
                    "top_snacks": snacks.order_by("-avg_overall_rating")[:5],
                    "popular_snacks": snacks.order_by("-review_count")[:5],
                    "interesting_facts": interesting_facts,
                    "user": current_user}
    return render_template('index.html', **context_dict)


""" Routes and methods related to user login and authentication """


@app.route('/register', methods=["GET", "POST"])
def register():
    # IMPORTANT: Encrypt the password for the increased security.
    encrypted_password = lambda password_as_string: bcrypt.generate_password_hash(password_as_string)
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm(request.form)
    if request.method == "POST":
        # Add user to database.
        if request.form['company_name'] != "":
            print(f"company user {form} \n")
            try:
                new_user = CompanyUser(email=request.form['email'], first_name=request.form['first_name'],
                                       last_name=request.form['last_name'], company_name=request.form['company_name'],
                                       password=encrypted_password(request.form['password']))
                new_user.save()
            except Exception as e:
                raise Exception\
                    (f"Error {e}. \n Couldn't add company user {new_user},\n with following registration form: {form}")
        else:
            print(f"normal user {form} \n")
            try:
                new_user = User(email=request.form['email'], first_name=request.form['first_name'],
                                last_name=request.form['last_name'], password=encrypted_password(request.form['password']))
                new_user.save()
            except Exception as e:
                raise Exception\
                    (f"Error {e}. \n Couldn't add user {new_user},\n with following registration form: {form}")
        login_user(new_user, remember=True)
        user = {
            'email': new_user.email,
            'first_name': new_user.first_name,
            'last_name': new_user.last_name,
            'company_name': new_user.last_name
        }
        response = make_response(json.dumps(user))
        response.status_code = 200
        print(f"register {response}\n")
        return response

    if request.args.get("email"):
        form.email.data = request.args.get("email")
    context_dict = {"title": "Register",
                    "form": form,
                    "user": current_user}
    return render_template("register.html", **context_dict)


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
            'last_name': current_user.last_name,
            'company_name': current_user.company_name
        }
        response = make_response(json.dumps(user))
        response.status_code = 200
        print(f"login {response}\n")
        return response

    context_dict = {"title": "Sign In",
                    "form": form,
                    "user": current_user}

    return render_template('login.html', **context_dict)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/create-review/<string:snack>", methods=["GET", "POST"])
@login_required
def create_review(snack):
    # Create a review and insert it into database.

    # check authenticated
    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    print("is_authenticated")

    review_form = CreateReviewForm(request.form)

    saltiness_review = review_form.saltiness.data
    sweetness_review = review_form.sweetness.data
    spiciness_review = review_form.spiciness.data
    bitterness_review = review_form.saltiness.data
    sourness_review = review_form.sourness.data
    overall_rating_review = review_form.overall_rating.data


    # post to db
    if request.method == "POST" and review_form.validate_on_submit():
        user_id = current_user.id
        snack_id = snack.split('=')[1]
        snackObject = Snack.objects(id=snack_id)

        # check if metric review
        if saltiness_review == 0 and sourness_review == 0 and spiciness_review == 0 \
            and bitterness_review == 0 and sweetness_review == 0:

            try:
                # user_id comes from current_user
                # snack_id should come from request sent by frontend
                # geolocation is found by request
                new_review = Review(user_id=user_id, snack_id=snack_id,
                                    description=review_form.description.data,
                                    geolocation="Default",
                                    overall_rating=overall_rating_review
                                    )
                new_review.save()

                avg_overall_rating = Review.objects.filter(snack_id=snack_id).average(
                    'overall_rating')

                snackObject.update(set__avg_overall_rating=avg_overall_rating)

                review_count = snackObject[0].review_count + 1
                snackObject.update(set__review_count=review_count)

            except Exception as e:
                raise Exception(
                    f"Error {e}. \n Couldn't add review {new_review},\n with following review form: {review_form}")

            print(f"A new user submitted the review form: {user_id}", file=sys.stdout)

            for u in Review.objects[:10]:
                print(u)

            return redirect(url_for('find_reviews_for_snack', filters=snack))

        # geolocation stuff
        # ip_address = request.access_route[0] or request.remote_addr
        # geodata = get_geodata(ip_address)
        # location = "{}, {}".format(geodata.get("city"),
        #                            geodata.get("zipcode"))
        else:
            try:
                # user_id comes from current_user
                # snack_id should come from request sent by frontend
                # geolocation is found by request
                snack_metric_review = MetricReview(user_id=user_id, snack_id=snack_id,
                                                   description=review_form.description.data,
                                                   geolocation="Default",
                                                   overall_rating=overall_rating_review,
                                                   sourness=sourness_review,
                                                   spiciness=spiciness_review,
                                                   saltiness=saltiness_review,
                                                   bitterness=bitterness_review,
                                                   sweetness=sweetness_review)
                snack_metric_review.save()

                avg_overall_rating = Review.objects.filter(snack_id=snack_id).average('overall_rating')
                avg_sourness = Review.objects.filter \
                    (Q(snack_id=snack_id) & Q(sourness__exists=True)).average("sourness")
                avg_spiciness = Review.objects.filter \
                    (Q(snack_id=snack_id) & Q(spiciness__exists=True)).average("spiciness")
                avg_bitterness = Review.objects.filter \
                    (Q(snack_id=snack_id) & Q(bitterness__exists=True)).average("bitterness")
                avg_sweetness = Review.objects.filter \
                    (Q(snack_id=snack_id) & Q(sweetness__exists=True)).average("sweetness")
                avg_saltiness = Review.objects.filter \
                    (Q(snack_id=snack_id) & Q(saltiness__exists=True)).average("saltiness")

                snackObject.update(set__avg_overall_rating=avg_overall_rating)
                snackObject.update(set__avg_sourness=avg_sourness)
                snackObject.update(set__avg_spiciness=avg_spiciness)
                snackObject.update(set__avg_bitterness=avg_bitterness)
                snackObject.update(set__avg_sweetness=avg_sweetness)
                snackObject.update(set__avg_saltiness=avg_saltiness)

                review_count = snackObject[0].review_count + 1
                snackObject.update(set__review_count=review_count)

            except Exception as e:
                raise Exception(
                    f"Error {e}. \n Couldn't add metric review {snack_metric_review},\n with following review form: {review_form}")

            print(f"A new user submitted the review form: {user_id}", file=sys.stdout)

            for u in MetricReview.objects[:10]:
                print(u)

            return redirect(url_for('find_reviews_for_snack', filters=snack))

    context_dict = {"title": "Create Review",
                    "form": review_form,
                    "user": current_user}
    # frontend stuff
    return render_template("create_review.html", **context_dict)


# Tested
# TODO: Need to still add image element
@app.route("/create-snack", methods=["GET", "POST"])
@login_required
def create_snack():
    # Get snacks from the database.

    if current_user.is_authenticated:
        print("User is authenticated")

        create_snack_form = CreateSnackForm(request.form)

        new_snack = None

        if request.method == "POST" and create_snack_form.validate_on_submit():
            snack_brand = create_snack_form.snack_brand.data
            snack_name = create_snack_form.snack_name.data

            print(snack_name)

            # Add snack to db

            if request.form['company_name'] != "":
                print(f"company user {form} \n")
                try:

                    new_snack = Snack(snack_name=create_snack_form.snack_name.data,
                                      available_at_locations=[create_snack_form.available_at_location.data],
                                      snack_brand=create_snack_form.snack_brand.data,
                                      category=create_snack_form.category.data,
                                      description=create_snack_form.description.data,
                                      is_verified=True,
                                      avg_overall_rating=0,
                                      avg_sourness=0,
                                      avg_spiciness=0,
                                      avg_bitterness=0,
                                      avg_sweetness=0,
                                      avg_saltiness=0,
                                      review_count=0
                                      )
                    new_snack.save()
                except Exception as e:
                    raise Exception(
                        f"Error {e}. \n Couldn't add {new_snack},\n with following creation form: {create_snack_form}")
                print(f"A new snack submitted the creation form: {snack_brand} => {snack_name}", file=sys.stdout)
            else:
                print(f"normal user {form} \n")
                try:
                    new_snack = Snack(snack_name=create_snack_form.snack_name.data,
                                      available_at_locations=[create_snack_form.available_at_location.data],
                                      snack_brand=create_snack_form.snack_brand.data,
                                      category=create_snack_form.category.data,
                                      description=create_snack_form.description.data,
                                      avg_overall_rating=0,
                                      avg_sourness=0,
                                      avg_spiciness=0,
                                      avg_bitterness=0,
                                      avg_sweetness=0,
                                      avg_saltiness=0,
                                      review_count=0
                                      )
                    new_snack.save()
                except Exception as e:
                    raise Exception(
                        f"Error {e}. \n Couldn't add {new_snack},\n with following creation form: {create_snack_form}")

                print(f"A new snack submitted the creation form: {snack_brand} => {snack_name}", file=sys.stdout)

            for snack in Snack.objects[:10]:
                print(snack)

            return redirect(url_for('index'))

        # For frontend purposes
        context_dict = {"title": "Create Snack",
                        "form": create_snack_form,
                        "user": current_user}

        return render_template("create_snack.html", **context_dict)
    else:
        # Go back to index if not authenticated
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
    snack_query = None
    # all reviews will be returned if nothing specified
    if "=" in filters:
        for individual_filter in all_filters:
            this_filter = individual_filter.split("=")
            query_index = this_filter[0]
            query_value = this_filter[1]
            if query_index == "user_id":
                queryset = queryset.filter(user_id=query_value)
            elif query_index == "snack_id":
                queryset = queryset.filter(snack_id=query_value)
                snack_query = Snack.objects(id=query_value)
            elif query_index == "overall_rating":
                queryset = queryset.filter(overall_rating__gte=query_value)
            elif query_index == "geolocation":
                queryset = queryset.filter(geolocation=query_value)
            elif query_index == "sourness":
                queryset = queryset.filter(sourness__gte=query_value)
            elif query_index == "spiciness":
                queryset = queryset.filter(spiciness__gte=query_value)
            elif query_index == "bitterness":
                queryset = queryset.filter(bitterness__gte=query_value)
            elif query_index == "sweetness":
                queryset = queryset.filter(sweetness__gte=query_value)
            elif query_index == "saltiness":
                queryset = queryset.filter(saltiness__gte=query_value)
    queryset = queryset.order_by("-overall_rating")
    print(f"snack_reviews: {queryset}", file=sys.stdout)
    print(f"snack_reviews: {snack_query}", file=sys.stdout)

    # Return results in a table, the metrics such as sourness are not displayed because if they are null, they give
    #   the current simple front end table an error, but it is there for use

    context_dict = {"query": snack_query,
                    "reviews": queryset,
                    "user": current_user}
    return render_template('reviews_for_snack.html', **context_dict)


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

    # the search string should be all if we want to get all snacks, but we can type anything that doesn't include '='
    # to get the same results
    if "=" in filters:
        for individual_filter in all_filters:
            this_filter = individual_filter.split("=")
            query_index = this_filter[0]
            query_value = this_filter[1]
            if query_index == "snack_name":
                # Change to contain so that snacks with similar name to inputted name will be returned too
                if query_value != "":
                    queryset = queryset.filter(snack_name__contains=query_value)
            elif query_index == "available_at_locations":
                # Note for this, say if they enter n, they will still return snacks in Canada because their contains
                #   is based on string containment. If order to solve this, we can let force users to select countries
                #   instead of typing countries
                if query_value != "all":
                    queryset = queryset.filter(available_at_locations__contains=query_value)
            elif query_index == "snack_brand":
                if query_value != "":
                    queryset = queryset.filter(snack_brand=query_value)
            elif query_index == "snack_company_name":
                queryset = queryset.filter(snack_company_name=query_value)
            elif query_index == "is_verified":
                if query_value == "false":
                    queryset = queryset.filter(is_verified=False)
                else:
                    queryset = queryset.filter(is_verified=True)
            elif query_index == "category":
                queryset = queryset.filter(category=query_value)
    queryset = queryset.order_by("snack_name")
    print(f"snack_reviews: {queryset}", file=sys.stdout)
    # TODO: What are the comments below?!
    # display = SnackResults(queryset)
    # display.border = True

    context_dict = {"query": queryset,
                    "user": current_user}
    # Return the same template as for the review, since it only needs to display a table.
    return render_template('search_query.html', **context_dict)


if __name__ == '__main__':
    app.run()
