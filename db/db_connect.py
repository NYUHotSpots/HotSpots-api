"""
This file contains some common MongoDB code.
"""
import os
import json
import logging as LOG
import pymongo as pm
import bson.json_util as bsutil
from dotenv import load_dotenv
from datetime import datetime

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
    output_spots = []
    for doc in all_spots_cursor:
        today = datetime.today().date().strftime('%Y-%m-%d')
        factorDate = doc["factorAvailability"]["factorDate"]
        if factorDate != today:
            print("DC Connect, Wrong date")
            spot_document = {}
            spot_document["factorAvailability"] = {
                "factorDate": datetime.today().date().strftime('%Y-%m-%d'),
                "factorValue": 0,
                "factorNumOfInputs": 0
            }
            doc["factorAvailability"] = {
                "factorDate": datetime.today().date().strftime('%Y-%m-%d'),
                "factorValue": 0,
                "factorNumOfInputs": 0
            }
            update_spot_factor(doc["_id"], spot_document)
        json_dump = json.dumps(doc, default=bsutil.default)
        output_spots.append(json.loads(json_dump))
    return output_spots


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

    today = datetime.today().date().strftime('%Y-%m-%d')
    factors = ["factorAvailability", "factorNoiseLevel",
               "factorTemperature", "factorAmbiance"]
    for factor in factors:
        factorDate = response[factor]["factorDate"]
        if factorDate != today:
            print("DB Connect, Wrong date for", factor)
            spot_document = {}
            newFactor = {
                "factorDate": datetime.today().date().strftime('%Y-%m-%d'),
                "factorValue": 0,
                "factorNumOfInputs": 0
            }
            spot_document[factor] = newFactor
            response[factor] = newFactor
            update_spot_factor(response["_id"], spot_document)
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
    print("Create Review", response)
    filter = {"_id": convert_to_object_id(spotID)}
    new_values = {"$push": {
        "reviews": review_object
    }}
    # try:
    spot_update = client[DB_NAME]['spots'].update_one(filter, new_values)
    LOG.info("Successfully updated spot" + str(spotID))
    print(spot_update)
    return str(review_object["_id"])


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


def get_review_by_spot(spot_id):
    review_cursor = client[DB_NAME]['reviews'].find({"spotID": spot_id})
    reviews = []
    for review in review_cursor:
        json_dump = json.dumps(review, default=bsutil.default)
        reviews.append(json.loads(json_dump))
    return reviews


def get_spot_factor(spot_id, factorName):
    query = {"_id": convert_to_object_id(spot_id)}
    projection = {factorName: 1}
    return client[DB_NAME]['spots'].find_one(query, projection)[factorName]


def update_spot_factor(spot_id, updateFactorDocument):
    filter = {"_id": convert_to_object_id(spot_id)}
    new_values = {"$set": updateFactorDocument}
    return client[DB_NAME]['spots'].update_one(filter, new_values)
