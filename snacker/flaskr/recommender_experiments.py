import urllib
from mongoengine import connect
from mongoengine.queryset.visitor import Q
import schema
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds
"""
The purpose of this file is to be used for experiments for the recommendation
algorithm of our application.

Important: Check the docs in deliverable/doc/recommender.md
"""

def recsys():
    DATABASE = "test"
    my_db = mongo[DATABASE]
    print(f"Connected to mongodb '{DATABASE}' database.")
    print(f"Collections found in the current database: {my_db.collection_names()}\n")
    training_data = generate_training_data(my_db)
    training_dataset(training_data)

def generate_training_data(my_db):
    """Given a database, generate training data from that specific database
       and return the data generated in a matrix in the form:
       user_index X snack_index, where:
       X[i][j] is the overall rating that user i gave to snack j."""
    collection_names = my_db.collection_names()
    # Check that we have the collections that we need
    assert "snack" in collection_names
    assert "review" in collection_names
    assert "user" in collection_names
    # Create mappers to map snack id to an index, and the reverse too
    snackID_to_index = {}
    index_to_snackID = {}
    index_snack = 0
    # Mapper for user
    userID_to_index = {}
    index_to_userID = {}
    index_user = 0
    # User ratings
    # user_index -> [(snack_index, ratingValue), (snack_index, ratingValue)]
    user_ratings = {}
    cursor = schema.User.objects.aggregate(*[
         {
          '$lookup': {
              'from': schema.Review._get_collection_name(),
              'localField': '_id',
              'foreignField': 'user_id',
              'as': 'review'}
         }])
    for c in cursor:
        # Add current user into the
        if not userID_to_index.get(str(c["_id"])):
            userID_to_index[str(c["_id"])] = index_user
            index_to_userID[index_user] =  str(c["_id"])
            # Empty list at first
            user_ratings[index_user] = []
        # If this user made a review, we need to add the ratings
        if c['review']:
            for review in c['review']:
                # Add current snack to the mapping if not already there
                if not snackID_to_index.get(str(review["snack_id"])):
                    snackID_to_index[str(review["snack_id"])] = index_snack
                    index_to_snackID[index_snack] =  str(review["snack_id"])
                    index_snack += 1
                user_ratings[index_user].append([snackID_to_index[str(review["snack_id"])], float(review["overall_rating"])])
            print(c['first_name'])
        index_user += 1
    # Create our training data
    row = []
    col = []
    data = []
    for user in user_ratings.keys():
        for rating in user_ratings[user]:
            #This is the logic: X[user, rating[0]] = rating[1]
            row.append(user)
            col.append(rating[0])
            data.append(rating[1])
    # Creating a sparse matrix to avoid HUGE memory usage
    X_sparse = csr_matrix((data, (row, col)), shape = (index_user, index_snack))
    print(f"Sparse matrix: \n{X_sparse}\n")
    # To convert to normal representation use toarray()
    print(f"Common rep. matrix: \n{X_sparse.toarray()}\n")
    # Returning an object with all the important information
    return {
        "X_sparse" : X_sparse,
        "snackID_to_index" : snackID_to_index,
        "index_to_snackID": index_to_snackID,
        "index_snack" :index_snack,
        "userID_to_index" : userID_to_index,
        "index_to_userID" : index_to_userID,
        "index_user" : index_user,
        "user_ratings" : user_ratings
    }

def training_dataset(training_data):
    # Supress scientific notation
    np.set_printoptions(suppress=True, linewidth=300)
    # IMPORTANT: Should be less than num rows and num cols!
    num_latent_features = 2
    #X_sparse = training_data["X_sparse"]
    X_sparse = np.array([   [5, 3, 0, 1],
                            [4, 0, 0, 1],
                            [1, 1, 0, 5],
                            [1, 0, 0, 4],
                            [0, 1, 5, 4],
                         ]).astype(float)
    user_ratings_mean = np.mean(X_sparse, axis = 1)
    R_demeaned = X_sparse - user_ratings_mean.reshape(-1, 1)
    U, sigma, Vt = svds(R_demeaned, k = num_latent_features)
    sigma = np.diag(sigma)
    all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
    #preds_df = pd.DataFrame(all_user_predicted_ratings, columns = R_df.columns)
    preds_df = pd.DataFrame(all_user_predicted_ratings)
    print(preds_df.head())
    # Testing for user 0
    num_recommendations = 4
    ratings = np.array(preds_df.iloc[0])
    # Negative because we want the max
    ind = np.argpartition(ratings, -num_recommendations)[-num_recommendations:]
    print(f"Recommendations for user [0]:")
    print(f"Indexes: {ind}")
    print(f"Ratings: {ratings[ind]}")
if __name__ == '__main__':
    try:
        mongo_uri = "mongodb://localhost:27017/"
        mongo = connect(host=mongo_uri)
    except Exception as inst:
        raise Exception("Error in database connection:", inst)
    recsys()

