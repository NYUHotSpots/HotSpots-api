"""
This file contains some common MongoDB code.
"""
import os
import json
import logging as LOG
import pymongo as pm
import bson.json_util as bsutil
import gridfs
from io import BytesIO
from bson.errors import InvalidId
from dotenv import load_dotenv
from datetime import datetime

from API.security.utils import json_abort
from db.models import RESET_FACTORS

load_dotenv()

username = os.environ.get("MONGO_USER")
cloud_db_url = os.environ.get("MONGO_URL")
passwd = os.environ.get("MONGO_PASSWORD")
cloud_mdb = "mongodb+srv"
db_params = "retryWrites=true&w=majority"


TEST_MODE = os.environ.get("TEST_MODE")
if TEST_MODE == "0":
    DB_NAME = os.environ.get("MONGO_DEV")
    URLNAME = "http://127.0.0.1:8000"
else:
    DB_NAME = os.environ.get("MONGO_PROD")
    URLNAME = "https://hotspotsapi.herokuapp.com"
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


def reset_factor():
    today = datetime.today().date().strftime('%Y-%m-%d')
    reset_factor = RESET_FACTORS
    reset_factor["factorDate"] = today
    return reset_factor


def check_document_exist(field, field_value, collection):
    cursor = list(client[DB_NAME][collection].find({field: field_value}))
    return cursor if len(cursor) > 0 else False


def get_all_spots():
    filter = {"spotName": {"$exists": True}}
    spots_cursor = client[DB_NAME]['spots'].find(filter)
    output_spots = []
    for doc in spots_cursor:
        today = datetime.today().date().strftime('%Y-%m-%d')
        factorDate = doc["factorDate"]
        if factorDate != today:
            print("DC Connect, Wrong date")
            new_spot_factors = reset_factor()
            update_spot_factor(doc["_id"], new_spot_factors)
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
    try:
        find_object = {"_id": convert_to_object_id(spot_id)}
        response = client[DB_NAME]['spots'].find_one(find_object)
        if not response:
            return None
        print("Fetch", response)
    except (pm.errors.CursorNotFound, InvalidId):
        LOG.error("Unable to find flavor with id " + spot_id)

    today = datetime.today().date().strftime('%Y-%m-%d')
    if response["factorDate"] != today:
        resetted = reset_factor()
        update_spot_factor(response["_id"], resetted)
    json_response = json.loads(json.dumps(response, default=bsutil.default))
    return json_response


def update_spot(spot_id, spot_document):
    """
    Update spot object to database
    """
    LOG.info("Attempting spot update")
    try:
        spot_id = convert_to_object_id(spot_id)
        spot = check_document_exist("_id", spot_id, "spots")
        if not spot:
            return None
        else:
            delete_spot_image(spot)
        filter = {"_id": spot_id}
        new_values = {"$set": spot_document}
        spot_update = client[DB_NAME]['spots'].update_one(filter, new_values)
        LOG.info("Successfully updated spot" + str(spot_id))
        print(spot_update)
        return spot_update
    except (pm.errors.CursorNotFound, InvalidId):
        LOG.error("Error occurred while updating DB, try again later")
        return None


def delete_spot(spot_id):
    """
    Delete spot from database
    """
    LOG.info("Attempting spot deletion")
    try:
        spot_id = convert_to_object_id(spot_id)
        spot = check_document_exist("_id", spot_id, "spots")
        if not spot:
            return None
        else:
            delete_spot_image(spot)            
        filter = {"_id": convert_to_object_id(spot_id)}
        spot_deletion = client[DB_NAME]['spots'].delete_one(filter)
        LOG.info("Successfully deleted spot " + str(spot_id))
        return spot_deletion
    except (pm.errors.CursorNotFound, InvalidId):
        LOG.error("Spot does not exist in DB")
        return None


def delete_spot_image(spot):
    image = spot[0]["spotImage"]
    if image and URLNAME in image:
        # delete the old image and save new one
        old_image_id = image.split("/")[-1]
        delete_file(old_image_id)


def create_review(spotID, review_object):
    try:
        spotID = convert_to_object_id(spotID)
        if not check_document_exist("_id", spotID, "spots"):
            return None
    except (pm.errors.CursorNotFound, InvalidId):
        return None
    response = client[DB_NAME]['reviews'].insert_one(review_object)
    print("Create Review", response)
    return str(review_object["_id"])


def delete_review(review_id, user_id, admin):
    LOG.info("Attempting review deletion")
    try:
        review_id = convert_to_object_id(review_id)
        review_cursor = check_document_exist("_id", review_id, "reviews")
        if not review_cursor:
            return None
        elif not admin:
            check_user_id_on_review(review_cursor, user_id)
        filter = {"_id": convert_to_object_id(review_id)}
        review_deletion = client[DB_NAME]['reviews'].delete_one(filter)
        LOG.info("Successfully deleted review " + str(review_id))
        return review_deletion
    except (pm.errors.CursorNotFound, InvalidId):
        LOG.info("Review does not exist in DB")
        return None


def get_review_by_spot(spot_id):
    try:
        review_cursor = check_document_exist("spotID", spot_id, "reviews")
        if not review_cursor:
            return None
    except (pm.errors.CursorNotFound, InvalidId):
        return None

    reviews = []
    for review in review_cursor:
        json_dump = json.dumps(review, default=bsutil.default)
        reviews.append(json.loads(json_dump))
    return reviews


def update_review(review_id, review_document, user_id):
    """
    Update review object to database
    """
    LOG.info("Attempting review update")
    try:
        review_id = convert_to_object_id(review_id)
        review_cursor = check_document_exist("_id", review_id, "reviews")
        if not review_cursor:
            return None
        else:
            check_user_id_on_review(review_cursor, user_id)
        filter = {"_id": review_id}
        new_values = {"$set": review_document}
        review_update = update_document(filter, new_values, "reviews")
        LOG.info("Successfully updated review" + str(review_id))
        print(review_update)
        return review_update
    except (pm.errors.CursorNotFound, InvalidId):
        return None


def check_user_id_on_review(review_cursor, user_id):
    for review in review_cursor:
        if review["userID"] != user_id:
            json_abort(403, {"message": "Permission denied"})


def update_document(filter, new_values, collection):
    try:
        return client[DB_NAME][collection].update_one(filter, new_values)
    except pm.errors.KeyNotFound:
        LOG.error("Flavor does not exist in DB")
        return None
    except pm.errors.UpdateOperationFailed:
        LOG.error("Error occurred while updating DB, try again later")
        return None


def get_spot_factor(spot_id, factorName):
    query = {"_id": convert_to_object_id(spot_id)}
    projection = {factorName: 1}
    return client[DB_NAME]['spots'].find_one(query, projection)[factorName]


def update_spot_factor(spot_id, updateFactorDocument):
    filter = {"_id": convert_to_object_id(spot_id)}
    new_values = {"$set": updateFactorDocument}
    return client[DB_NAME]['spots'].update_one(filter, new_values)


def save_file(name, file):
    gfs = gridfs.GridFS(client[DB_NAME])
    id = gfs.put(file, filename=name)
    return id


def delete_file(id):
    try:
        id = convert_to_object_id(id)
        client[DB_NAME]['fs.files'].delete_one({"_id": id})
        client[DB_NAME]['fs.chunks'].delete_one({"files_id": id})
    except (pm.errors.CursorNotFound, InvalidId):
        LOG.error("Error occurred with deleting file {id}")
        return None


def fetch_file(id):
    # open_download_stream_by_name
    try:
        id = convert_to_object_id(id)
        gfs = gridfs.GridFSBucket(client[DB_NAME])
        grid_out = gfs.open_download_stream(id)
        image = grid_out.read()
        filename = client[DB_NAME]['fs.files'].find_one({"_id": id})
        return (BytesIO(image), filename["filename"])
    except (pm.errors.CursorNotFound, InvalidId, gridfs.errors.NoFile):
        LOG.error("trouble fetching file")
        return
