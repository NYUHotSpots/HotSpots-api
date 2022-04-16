# from hashlib import new
import os
import db.db_connect as dbc
from db.models import SPOT_FACTORS
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TEST_MODE = os.environ.get("TEST_MODE")

if TEST_MODE == "0":
    DB_NAME = os.environ.get("MONGO_DEV")
    URLNAME = "http://127.0.0.1:8000"
else:
    DB_NAME = os.environ.get("MONGO_PROD")
    URLNAME = "https://hotspotsapi.herokuapp.com"

print("Using DB:", DB_NAME)

OK = 0
NOT_FOUND = 1
DUPLICATE = 2

client = dbc.get_client()
print(client)


def get_spots():
    """
    return all spots in spots collection
    """
    return dbc.get_all_spots()


def add_spot(spotName, spotAddress, spotCapacity, spotImage, spotImageUpload):
    """
    create a new spot document
    """
    if spotImageUpload:
        print("hi")
        filename = spotImageUpload.filename
        print(f"{filename=}")
        id = str(dbc.save_file(filename, spotImageUpload))
        spotImage = f"{URLNAME}/file/{id}"
    
    today = datetime.today().date().strftime('%Y-%m-%d')
    now = str(datetime.now())
    print("Creating new spot document")
    print("Today is", today)
    spot_document = {
        "spotName": spotName,
        "spotImage": spotImage,
        "spotAddress": spotAddress,
        "spotCapacity": spotCapacity,
        "spotCreation": now,
        "spotUpdate": now,
        "factorAvailability": 0,
        "factorNoiseLevel": 0,
        "factorTemperature": 0,
        "factorAmbiance": 0,
        "numFactorEntries": 0,
        "factorDate": today
    }

    response = dbc.create_spot(spot_document)
    print("Add Spot Response:", response)
    if response is None:
        return DUPLICATE
    return response


def get_spot_detail(spot_id):
    response = dbc.fetch_spot_details(spot_id)
    if response is None:
        return NOT_FOUND
    reviews = get_review_by_spot(spot_id)
    if reviews is not NOT_FOUND:
        response["reviews"] = reviews
    return response


def update_spot(spot_id, spotName, spotAddress, spotCapacity, spotImage):
    """
    Update spot attribute
    """
    spot_document = {
        "spotName": spotName,
        "spotImage": spotImage,
        "spotAddress": spotAddress,
        "spotCapacity": spotCapacity,
        "spotUpdate": str(datetime.now())
    }
    response = dbc.update_spot(spot_id, spot_document)
    if response is None:
        return NOT_FOUND
    return response


def update_spot_factors(spot_id, factor_update):
    spot_id = dbc.convert_to_object_id(spot_id)
    spot_document = dbc.check_document_exist("_id", spot_id, "spots")
    if not spot_document:
        return NOT_FOUND
    # we won't have more than one bc we look by id
    new_spot_doc = spot_document[0]
    today = datetime.today().date()
    date = datetime.strptime(new_spot_doc["factorDate"], '%Y-%m-%d').date()
    if date != today:
        # reset everything to 0, doesn't matter for the average
        print("Resetting factors with today's data: %s", today)
        new_spot_doc["numFactorEntries"] = 0
        new_spot_doc["factorDate"] = today
        for f_field in SPOT_FACTORS:
            new_spot_doc[f_field] = 0

    N = new_spot_doc["numFactorEntries"]
    new_spot_doc["numFactorEntries"] += 1
    for f_field in SPOT_FACTORS:
        old_avg = new_spot_doc[f_field]
        new_value = factor_update[f_field]
        if new_value < 1:
            new_value = 0
        elif new_value > 5:
            new_value = 5
        new_spot_doc[f_field] = get_average(old_avg, N, new_value)

    dbc.update_spot_factor(spot_id, new_spot_doc)
    return spot_id


def get_average(old_average, n, new_value):
    return ((old_average * n) + new_value)/(n+1)


def delete_spot(spot_id):
    """
    Deletes a flavor
    """
    response = dbc.delete_spot(spot_id)
    if response is None:
        return NOT_FOUND
    return response


def add_review(spotID, reviewTitle, reviewText, reviewRating, user_id):
    """
    Return a dictionary of created review.
    """
    review_object = {
        "_id": dbc.generate_id(),
        "spotID": spotID,
        "reviewCreation": str(datetime.now()),
        "reviewUpdate": str(datetime.now()),
        "reviewTitle": reviewTitle,
        "reviewText": reviewText,
        "reviewRating": reviewRating,
        "userID": user_id
    }
    print("Create review object", review_object)
    response = dbc.create_review(spotID, review_object)
    if not response:
        return NOT_FOUND
    print("Add Review response: ", response)
    return response


def delete_review(reviewID, user_id, admin):
    """
    Deletes a review
    """
    response = dbc.delete_review(reviewID, user_id, admin)
    if response is None:
        return NOT_FOUND
    return response


def get_review_by_spot(spot_id):
    """
    Get review by spot id
    """
    response = dbc.get_review_by_spot(spot_id)
    return response if response is not None else NOT_FOUND


def update_review(review_id, spot_id, reviewTitle,
                  reviewText, reviewRating, user_id):
    review_document = {
        "spotID": spot_id,
        "reviewTitle": reviewTitle,
        "reviewText": reviewText,
        "reviewRating": reviewRating,
        "reviewUpdate": str(datetime.now())
    }
    response = dbc.update_review(review_id, review_document, user_id)
    if response is None:
        return NOT_FOUND
    return response

def get_file(file_id):
    return dbc.fetch_file(file_id)