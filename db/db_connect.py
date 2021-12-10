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
        # uri = f"mongodb://{cloud_db_url}:{username}@{passwd}"
        uri = f"mongodb+srv://{username}:{passwd}@{cloud_db_url}/ice_cream_emporium_prod?{db_params}"
        
        client = pm.MongoClient(uri)
        # client = pm.MongoClient(f"mongodb://{username}:{passwd}.@{cloud_db_url}"
        #                         + f"/{DB_NAME}?{db_params}")
    return client


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


def generate_id():
    """
    Generates a Mongo ObjectID
    """
    return bsutil.ObjectId()


def create_flavor(flavor_object):
    """
    Adds a new flavor object to the database
    """
    return client[DB_NAME]['flavor'].insert_one(flavor_object)