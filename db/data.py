# from hashlib import new
import os
import db.db_connect as dbc
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

TEST_MODE = os.environ.get("TEST_MODE")

if TEST_MODE == "0":
    DB_NAME = os.environ.get("MONGO_DEV")
else:
    DB_NAME = os.environ.get("MONGO_PROD")

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


def add_spot(spotName, spotAddress, spotCapacity, spotImage):
    """
    create a new spot document
    """
    print("Creating new spot document")
    print("Today is", datetime.today().date().strftime('%Y-%m-%d'))
    spot_document = {
        "spotName": spotName,
        "spotImage": spotImage,
        "spotAddress": spotAddress,
        "spotCapacity": spotCapacity,
        "spotCreation": str(datetime.now()),
        "spotUpdate": str(datetime.now()),
        "factorAvailability": {
            "factorDate": datetime.today().date().strftime('%Y-%m-%d'),
            "factorValue": 0,
            "factorNumOfInputs": 0
        },
        "factorNoiseLevel": {
            "factorDate": datetime.today().date().strftime('%Y-%m-%d'),
            "factorValue": 0,
            "factorNumOfInputs": 0
        },
        "factorTemperature": {
            "factorDate": datetime.today().date().strftime('%Y-%m-%d'),
            "factorValue": 0,
            "factorNumOfInputs": 0
        },
        "factorAmbiance": {
            "factorDate": datetime.today().date().strftime('%Y-%m-%d'),
            "factorValue": 0,
            "factorNumOfInputs": 0
        },
        "reviews": []
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
    return response


def update_spot(spot_id, spotName, spotAddress, spotCapacity, spotImage):
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


def update_individual_spot_factor(spot_id, factorName, factorRating):
    if not (1 <= factorRating <= 10):
        return
    spotFactor = dbc.get_spot_factor(spot_id, factorName)
    today = datetime.today().date()

    spot_document = {}
    spot_document["spotUpdate"] = str(datetime.now())

    # if dates are not the same, then new day has begun
    # need to reset data with current input
    if datetime.strptime(spotFactor["factorDate"], '%Y-%m-%d').date() != today:
        print("Resetting factors with today's data: %s", today)
        spot_document[factorName] = {
            "factorDate": datetime.today().date().strftime('%Y-%m-%d'),
            "factorValue": factorRating,
            "factorNumOfInputs": 1
        }
        dbc.update_spot_factor(spot_id, spot_document)
    # if day is still going on, need to average out new input
    else:
        print("Correct date")
        currentRating = spotFactor["factorValue"]
        currentCount = spotFactor["factorNumOfInputs"]
        newCount = currentCount + 1
        newRatingAverage = ((currentRating*currentCount)+factorRating)/newCount
        spot_document[factorName] = {
            "factorDate": datetime.today().date().strftime('%Y-%m-%d'),
            "factorValue": newRatingAverage,
            "factorNumOfInputs": newCount
        }
        dbc.update_spot_factor(spot_id, spot_document)


def update_spot_factors(spot_id, factorArgs):
    spot_id = dbc.convert_to_object_id(spot_id)
    if not dbc.check_document_exist("_id", spot_id, "spots"):
        return NOT_FOUND
    for factor in factorArgs:
        rating = int(factorArgs[factor]["factorValue"])
        update_individual_spot_factor(spot_id, factor, rating)

    return spot_id


def delete_spot(spot_id):
    """
    Deletes a flavor
    """
    response = dbc.delete_spot(spot_id)
    if response is None:
        return NOT_FOUND
    return response


def add_review(spotID, reviewTitle, reviewText, reviewRating):
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
        "reviewRating": reviewRating
    }
    print("Create review object", review_object)
    response = dbc.create_review(spotID, review_object)
    if not response:
        return NOT_FOUND
    print("Add Review response: ", response)
    return response


def delete_review(reviewID):
    """
    Deletes a review
    """
    response = dbc.delete_review(reviewID)
    if response is None:
        return NOT_FOUND
    return response


def get_review_by_spot(spot_id):
    """
    Get review by spot id
    """
    response = dbc.get_review_by_spot(spot_id)
    return response if response is not None else NOT_FOUND


def update_review(review_id, spot_id, reviewTitle, reviewText, reviewRating):
    review_document = {
        "spotID": spot_id,
        "reviewTitle": reviewTitle,
        "reviewText": reviewText,
        "reviewRating": reviewRating,
        "reviewUpdate": str(datetime.now())
    }
    response = dbc.update_review(review_id, review_document)
    if response is None:
        return NOT_FOUND
    return response
