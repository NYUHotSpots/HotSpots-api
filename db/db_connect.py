"""
This file contains some common MongoDB code.
"""
import os
import json
import pymongo as pm
import bson.json_util as bsutil

username = "prof"
cloud_db_url = "cluster0.xjsf0.mongodb.net"
passwd = os.environ.get("MONGO_PASSWD", '')
print("Password", passwd)
cloud_mdb = "mongodb+srv"
db_params = "retryWrites=true&w=majority"


TEST_MODE = os.environ.get("TEST_MODE", 0)
if TEST_MODE == 0:
    # this one should be changed!
    DB_NAME = "ice_cream_emporium_dev"
else:
    DB_NAME = "ice_cream_emporium_prod"
# print("Using DB:", DB_NAME)


client = None


def get_client():
    """
    This provides a uniform way to get the client across all uses.
    Returns a mongo client object... maybe we shouldn't?
    Also set global client variable.
    """
    global client
    LOCAL_MONGO = os.environ.get("LOCAL_MONGO", 1)
    if LOCAL_MONGO == 1:
        print("Local Mongo")
        client = pm.MongoClient()
    else:
        uri = f"mongodb+srv://{username}:{passwd}@{cloud_db_url}/ice_cream_emporium_prod?{db_params}"
        client = pm.MongoClient(uri)
    return client


def generate_id():
    """
    Generates a Mongo ObjectID
    """
    return bsutil.ObjectId()


def convert_to_object_id(flavor_id):
    """
    Convert to a Mongo ObjectID
    """
    return bsutil.ObjectId(flavor_id)


def fetch_all_flavors():
    """
    Returns a dictionary object of all flavors matching id to flavorName
    """
    all_flavors = dict()
    print("Fetching All Flavors")
    flavors = client[DB_NAME]["flavor"].find()
    for flavor in flavors:
        id = str(flavor["_id"])
        name = flavor["flavorName"]
        all_flavors[id] = name
    return all_flavors


def fetch_flavor_details(flavor_id):
    find_object = {"_id": convert_to_object_id(flavor_id)}
    response = client[DB_NAME]['flavor'].find_one(find_object)
    json_response = json.loads(bsutil.dumps(response))
    flavor_object = {
        "flavorID": json_response["_id"]["$oid"],
        "flavorName": json_response["flavorName"],
        "flavorImage": json_response["flavorImage"],
        "flavorDescription": json_response["flavorDescription"],
        "flavorNutrition": json_response["flavorNutrition"],
        "flavorPrice": json_response["flavorPrice"],
        "flavorAvailability": json_response["flavorAvailability"]
    }
    return flavor_object


def create_flavor(flavor_object):
    """
    Adds a new flavor object to the database
    """
    return client[DB_NAME]['flavor'].insert_one(flavor_object)


def update_flavor(flavor_id, flavor_object):
    """
    Update flavor object to database
    """
    filter = {"_id": convert_to_object_id(flavor_id)}
    new_values = { "$set": flavor_object }
    try:
        return client[DB_NAME]['flavor'].update_one(filter, new_values)
    except:
        return None

def delete_flavor(flavor_id):
    """
    Delete flavor from database
    """
    filter = {"_id": convert_to_object_id(flavor_id)}
    try:
        return client[DB_NAME]['flavor'].delete_one(filter)
    except:
        return None
