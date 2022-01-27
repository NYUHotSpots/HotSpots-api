"""
This file contains some common MongoDB code.
"""
import os
import json
import logging as LOG
import pymongo as pm
import bson.json_util as bsutil
from dotenv import load_dotenv

load_dotenv()

username = os.environ.get("MONGO_USER")
cloud_db_url = os.environ.get("MONGO_URL")
passwd = os.environ.get("MONGO_PASSWORD")
cloud_mdb = "mongodb+srv"
db_params = "retryWrites=true&w=majority"


TEST_MODE = os.environ.get("TEST_MODE")
if TEST_MODE == "0":
    DB_NAME = os.environ.get("MONGO_DEV")
else:
    DB_NAME = os.environ.get("MONGO_PROD")
print("Using DB:", DB_NAME)


client = None


def get_client():
    """
    This provides a uniform way to get the client across all uses.
    Returns a mongo client object... maybe we shouldn't?
    Also set global client variable.
    """
    global client
    LOCAL_DB = os.environ.get("LOCAL_DB")
    print("LOCAL_DB", LOCAL_DB)
    if LOCAL_DB == "0":
        LOG.info("Local DB")
        client = pm.MongoClient()
    else:
        client = pm.MongoClient(f"mongodb+srv://{username}:{passwd}"
                                + f"@{cloud_db_url}/" + DB_NAME
                                + f"?{db_params}", connect=False)
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


def get_all_spots():
    all_spots_cursor = client[DB_NAME]['spots'].find(
        {}, {"spotName": 1, "spotAddress": 1,
             "spotImage": 1, "factorAvailability": 1})
    all_spots = [json.loads(json.dumps(doc, default=bsutil.default))
                 for doc in all_spots_cursor]
    return all_spots


def create_spot(spot_document):
    """
    Adds a new spot document to collection
    """
    LOG.info("Attempting spot creation")
    try:
        client[DB_NAME]['spots'].insert_one(spot_document)
        LOG.info("Successfully created flavor " + str(spot_document["_id"]))
        return str(spot_document["_id"])
    except pm.errors.DuplicateKeyError:
        LOG.error("Duplicate key, unable to create existing flavor")
        return None


def fetch_spot_details(spot_id):
    find_object = {"_id": convert_to_object_id(spot_id)}
    try:
        response = client[DB_NAME]['spots'].find_one(find_object)
        print("Fetch", response)
    except pm.errors.KeyNotFound:
        LOG.error("Unable to find flavor with id " + spot_id)
    json_response = json.loads(json.dumps(response, default=bsutil.default))
    return json_response


def update_spot(spot_id, spot_document):
    """
    Update spot object to database
    """
    filter = {"_id": convert_to_object_id(spot_id)}
    new_values = {"$set": spot_document}
    LOG.info("Attempting spot update")
    try:
        spot_update = client[DB_NAME]['spots'].update_one(filter, new_values)
        LOG.info("Successfully updated spot" + str(spot_id))
        print(spot_update)
        return spot_update
    except pm.errors.KeyNotFound:
        LOG.error("Flavor does not exist in DB")
        return None
    except pm.errors.UpdateOperationFailed:
        LOG.error("Error occurred while updating DB, try again later")
        return None


def delete_spot(spot_id):
    """
    Delete spot from database
    """
    filter = {"_id": convert_to_object_id(spot_id)}
    LOG.info("Attempting spot deletion")
    try:
        spot_deletion = client[DB_NAME]['spots'].delete_one(filter)
        LOG.info("Successfully deleted spot " + str(spot_id))
        return spot_deletion
    except pm.errors.KeyNotFound:
        LOG.error("Spot does not exist in DB")
        return None


def create_review(spotID, review_object):
    response = client[DB_NAME]['reviews'].insert_one(review_object)
    print("Create REview", response)
    filter = {"_id": convert_to_object_id(spotID)}
    new_values = {"$push": {
        "reviews": review_object
    }}
    # try:
    spot_update = client[DB_NAME]['spots'].update_one(filter, new_values)
    LOG.info("Successfully updated spot" + str(spotID))
    print(spot_update)
    return spot_update

    # except pm.errors.KeyNotFound:
    #     LOG.error("Spot does not exist in DB")
    #     return None
    # except pm.errors.UpdateOperationFailed:
    #     LOG.error("Error occurred while updating DB, try again later")
    #     return None


def delete_review(reviewID):
    filter = {"_id": convert_to_object_id(reviewID)}
    LOG.info("Attempting review deletion")
    try:
        review_deletion = client[DB_NAME]['reviews'].delete_one(filter)
        LOG.info("Successfully deleted review " + str(reviewID))
        return review_deletion
    except pm.errors.KeyNotFound:
        LOG.error("Review does not exist in DB")
        return None
