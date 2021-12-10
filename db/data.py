"""
This file will manage interactions with our data store.
At first, it will just contain stubs that return fake data.
Gradually, we will fill in actual calls to our datastore.
"""

import os
import re
import db.db_connect as dbc

ICECREAMPATH = os.environ["IceCreamPath"]
TEST_MODE = os.environ.get("TEST_MODE", 0)

if TEST_MODE == 0:
    DB_NAME = "ice_cream_emporium_dev"
else:
    DB_NAME = "ice_cream_emporium_prod"
print("Using DB:", DB_NAME)

ROOMS = "rooms"
USERS = "users"

# field names in our DB:
USER_NM = "userName"
ROOM_NM = "roomName"
NUM_USERS = "num_users"

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
    if response == None:
        return NOT_FOUND
    return response
    

def add_flavor(flavor_name, flavor_image, flavor_description, flavor_nutrition, flavor_price, flavor_availability):
    """
    Return a dictionary of created flavors.
    """
    flavor_object = {
        "_id": dbc.generate_id(),
        "flavorName": flavor_name,
        "flavorImage": flavor_image,
        "flavorDescription": flavor_description,
        "flavorNutrition": flavor_nutrition,
        "flavorPrice": flavor_price,
        "flavorAvailability": flavor_availability
    }
    print("Create flavor object", flavor_object)
    return dbc.create_flavor(flavor_object)


def check_flavor_exists(flavorID):
    flavors = get_flavors()
    return flavorID in flavors


def update_flavor(flavor_id, flavor_name, flavor_image, flavor_description, flavor_nutrition, flavor_price, flavor_availability):
    """
    Return a dictionary of updated flavor.
    """
    flavor_object = {
        "flavorName": flavor_name,
        "flavorImage": flavor_image,
        "flavorDescription": flavor_description,
        "flavorNutrition": flavor_nutrition,
        "flavorPrice": flavor_price,
        "flavorAvailability": flavor_availability
    }
    print("Updated flavor object", flavor_object)
    response = dbc.update_flavor(flavor_id, flavor_object)
    if response == None:
        return NOT_FOUND
    return response


def delete_flavor(flavor_id):
    """
    Deletes a flavor
    """
    response = dbc.delete_flavor(flavor_id)
    if response == None:
        return NOT_FOUND
    return response