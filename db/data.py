from hashlib import new
import os
import db.db_connect as dbc
from dotenv import load_dotenv
from datetime import date, datetime

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
        "spotCapacity": spotCapacity
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
    spot_document["spotUpdate"] = str(datetime.datetime.now())
    
    # if dates are not the same, then new day has begun, need to reset data with current input
    if datetime.strptime(spotFactor["factorDate"], '%Y-%m-%d').date() != today:
        print("Wrong date")
        spot_document[factorName] = {
            "factorDate": datetime.today().date().strftime('%Y-%m-%d'),
            "factorValue": factorRating,
            "factorNumOfInputs": 1
        }
        dbc.update_spot_factor(spot_id, spot_document)
    # if day is still going on, need to average out new input
    else:
        print("Correct date")
        # print(datetime.today().date())
        # print(datetime.strptime(spotFactor["factorDate"], '%Y-%m-%d').date())
        currentRating = spotFactor["factorValue"]
        currentCount = spotFactor["factorNumOfInputs"]
        newCount = currentCount + 1
        newRating = ((currentRating * currentCount) + factorRating) / newCount # find new average of ratings
        spot_document[factorName] = {
            "factorDate": datetime.today().date().strftime('%Y-%m-%d'),
            "factorValue": newRating,
            "factorNumOfInputs": newCount
        }
        dbc.update_spot_factor(spot_id, spot_document)


def update_spot_factors(spot_id, factorArgs):
    for factor in factorArgs:
        update_individual_spot_factor(spot_id, factor, factorArgs[factor])
    return spot_id


def delete_spot(spot_id):
    """
    Deletes a flavor
    """
    response = dbc.delete_spot(spot_id)
    if response is None:
        return NOT_FOUND
    return response


def update_factors(spot_id, factorAvailability=None,
                   factorNoiseLevel=None,
                   factorTemperature=None,
                   factorAmbiance=None):
    spot_document = {}
    if factorAvailability:
        spot_document["factorAvailability"] = factorAvailability
    if factorNoiseLevel:
        spot_document["factorNoiseLevel"] = factorNoiseLevel
    if factorTemperature:
        spot_document["factorTemperature"] = factorTemperature
    if factorAmbiance:
        spot_document["factorAmbiance"] = factorAmbiance

    response = dbc.update_spot(spot_id, spot_document)
    return response if response is not None else NOT_FOUND


def add_review(spotID, reviewDate, reviewTitle, reviewText, reviewRating):
    """
    Return a dictionary of created review.
    """
    review_object = {
        "_id": dbc.generate_id(),
        "spotID": spotID,
        "reviewDate": reviewDate,
        "reviewTitle": reviewTitle,
        "reviewText": reviewText,
        "reviewRating": reviewRating
    }
    print("Create review object", review_object)
    return dbc.create_review(spotID, review_object)


def delete_review(reviewID):
    """
    Deletes a review
    """
    response = dbc.delete_review(reviewID)
    if response is None:
        return NOT_FOUND
    return response
