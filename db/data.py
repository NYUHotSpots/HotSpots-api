"""
This file will manage interactions with our data store.
At first, it will just contain stubs that return fake data.
Gradually, we will fill in actual calls to our datastore.
"""

import os
# import re
import db.db_connect as dbc

ICECREAMPATH = os.environ["IceCreamPath"]
TEST_MODE = os.environ.get("TEST_MODE", 0)

if TEST_MODE == "0":
    DB_NAME = "ice_cream_emporium_dev"
else:
    DB_NAME = "ice_cream_emporium_prod"
print("Using DB:", DB_NAME)

OK = 0
NOT_FOUND = 1
DUPLICATE = 2

client = dbc.get_client()
print(client)


def get_flavors():
    """
    Return a list of all flavors.
    """
    return dbc.fetch_all_flavors()


def get_flavor_detail(flavor_id):
    response = dbc.fetch_flavor_details(flavor_id)
    if response is None:
        return NOT_FOUND
    return response


def add_flavor(flavor_object):
    """
    Return a dictionary of created flavors.
    """
    print("Create flavor object", flavor_object)
    response = dbc.create_flavor(flavor_object)
    if response is None:
        return DUPLICATE
    return response


def check_flavor_exists(flavorID):
    flavors = get_flavors()
    return flavorID in flavors


def update_flavor(flavor_id, flavor_object):
    """
    Return a dictionary of updated flavor.
    """
    print("Updated flavor object", flavor_object)
    response = dbc.update_flavor(flavor_id, flavor_object)
    if response is None:
        return NOT_FOUND
    return response


def delete_flavor(flavor_id):
    """
    Deletes a flavor
    """
    response = dbc.delete_flavor(flavor_id)
    if response is None:
        return NOT_FOUND
    return response


def add_review(review_name, flavor_id, review_text):
    """
    Return a dictionary of created review.
    """
    review_object = {
        "_id": dbc.generate_id(),
        "reviewName": review_name,
        "flavorID": flavor_id,
        "reviewText": review_text
    }
    print("Create review object", review_object)
    return dbc.create_review(review_object)
