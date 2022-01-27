from cgitb import Hook
import os
from unittest import TestCase

from pyrsistent import T
import db.db_connect as dbc
from dotenv import load_dotenv

load_dotenv()

HOTSPOTS_PATH = os.environ.get("HOTSPOTS_PATH")
TEST_MODE = os.environ.get("TEST_MODE")

print("PATH + TESTMODE", HOTSPOTS_PATH, TEST_MODE)

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
    spot_document = {
        "spotName": spotName,
        "spotImage": spotImage,
        "spotAddress": spotAddress,
        "spotCapacity": spotCapacity,
        "factorAvailability": {
            "factorDate": "",
            "factorValue": 0,
            "factorNumOfInputs": 0
        },
        "factorNoiseLevel": {
            "factorDate": "",
            "factorValue": 0,
            "factorNumOfInputs": 0
        },
        "factorTemperature": {
            "factorDate": "",
            "factorValue": 0,
            "factorNumOfInputs": 0
        },
        "factorAmbiance": {
            "factorDate": "",
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


def delete_spot(spot_id):
    """
    Deletes a flavor
    """
    response = dbc.delete_spot(spot_id)
    if response is None:
        return NOT_FOUND
    return response


def add_review(spotID, reviewDate, reviewTitle, reviewText):
    """
    Return a dictionary of created review.
    """
    review_object = {
        "_id": dbc.generate_id(),
        "reviewDate": reviewDate,
        "reviewTitle": reviewTitle,
        "reviewText": reviewText
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