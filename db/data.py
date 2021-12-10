"""
This file will manage interactions with our data store.
At first, it will just contain stubs that return fake data.
Gradually, we will fill in actual calls to our datastore.
"""

import os
import db

import db.db_connect as dbc

ICECREAMPATH = os.environ["IceCreamPath"]
TEST_MODE = os.environ.get("TEST_MODE", 0)

if TEST_MODE == 0:
    # this one should be changed!
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
    A function to return a list of all flavors.
    """
    return dbc.fetch_all_flavors()


def add_flavor(flavor_name, flavor_image, flavor_description, flavor_nutrition, flavor_price, flavor_availability):
    """
    A function to return a dictionary of all flavors.
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


def room_exists(roomname):
    rooms = get_rooms()
    return roomname in rooms


def del_room(roomname):
    """
    Delete roomname from the db.
    """
    if not room_exists(roomname):
        return NOT_FOUND
    return OK


def add_room(roomname):
    """
    Add a room to the room database.
    """
    rooms = get_rooms()
    if rooms is None:
        return NOT_FOUND
    elif roomname in rooms:
        return DUPLICATE
    else:
        rooms[roomname] = {"num_users": 0}
        dbc.insert_doc(ROOMS, {ROOM_NM: roomname, NUM_USERS: 0})
        return OK


def get_users():
    """
    A function to return a dictionary of all users.
    """
    return dbc.fetch_all(USERS, USER_NM)


def add_user(username):
    """
    Add a user to the user database.
    Until we are using a real DB, we have a potential
    race condition here.
    """
    users = get_users()
    if users is None:
        return NOT_FOUND
    elif username in users:
        return DUPLICATE
    else:
        dbc.insert_doc(USERS, {USER_NM: username})
        return OK
