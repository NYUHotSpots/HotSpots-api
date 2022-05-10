"""
This file holds the tests for db.py.
"""

from unittest import TestCase, skip
import db.data as db
import db_connect as dbc
from io import BytesIO
from pymongo.results import UpdateResult, DeleteResult
import bson.json_util as bsutil

# SPOT TEST DATA
TEST_SPOT_NAME = "TEST_DATA SPOT NAME"
TEST_SPOT_IMAGE = "TEST_DATA SPOT IMAGE URL"
TEST_SPOT_ADDR = "TEST_DATA SPOT ADDRESS"
TEST_SPOT_CAPACITY = "TEST_DATA SPOT CAPACITY"

# REVIEW TEST DATA
TEST_REVIEW_SPOT_ID = None 
# for now, it's none because we make it when we insert a spot
TEST_REVIEW_TITLE = "TEST_DATA REVIEW TTILE"
TEST_REVIEW_TEXT = "TEST_DATA REVIEW TEXT"
TEST_REVIEW_RATING = 1

# FACTOR TEST DATA
TEST_FACTOR_AVAILABILITY = 1
TEST_FACTOR_NOISE_LEVEL = 1
TEST_FACTOR_TEMP = 1 
TEST_FACTOR_AMBI = 1

client = dbc.get_client()

class DBTestCase(TestCase):
    def setUp(self):
        print("SETUP")
        self.TEST_SPOT_DOC = {
        "spotName": TEST_SPOT_NAME,
        "spotImage": TEST_SPOT_IMAGE,
        "spotAddress": TEST_SPOT_ADDR,
        "spotCapacity": TEST_SPOT_CAPACITY,
        "spotCreation": "2022-05-09",
        "spotUpdate": "2022-05-09",
        "factorAvailability": TEST_FACTOR_AVAILABILITY,
        "factorNoiseLevel": TEST_FACTOR_NOISE_LEVEL,
        "factorTemperature": TEST_FACTOR_TEMP,
        "factorAmbiance": TEST_FACTOR_AMBI,
        "numFactorEntries": 1,
        "factorDate": "2022-05-09"
        }
        self.TEST_REVIEW_DOC = {
                "_id": dbc.generate_id(),
                "reviewCreation": "2022-05-09",
                "reviewUpdate": "2022-05-09",
                "reviewTitle": TEST_REVIEW_TITLE,
                "reviewText": TEST_REVIEW_TEXT,
                "reviewRating": TEST_REVIEW_RATING,
                "userID": "abcde"
        }
        self.spot_id = dbc.create_spot(self.TEST_SPOT_DOC)
        self.TEST_REVIEW_DOC["spotID"] = self.spot_id
        self.review_id = dbc.create_review(self.spot_id, self.TEST_REVIEW_DOC)
        print(self.spot_id, self.review_id)
        self.ids_to_delete = {"review_id": self.review_id, 
                              "spot_id": self.spot_id}
        

    def tearDown(self):
        print("TEARDOWN")
        if self.ids_to_delete.get("spot_id"):
            # deleting a spot deletes associated reviews
            dbc.delete_spot(self.ids_to_delete["spot_id"])
        elif self.ids_to_delete.get("review_id"):
            dbc.delete_review(self.ids_to_delete["review_id"], None, True)

    def test_get_spots(self):
        """
        Tests the database to see if we can get spots
        """
        spots = db.get_spots()
        self.assertIsInstance(spots, list)

    def test_get_review(self):
        """
        Tests if we can get reviews of a spot
        """
        reviews = db.get_review_by_spot(self.spot_id)
        self.assertIsInstance(reviews, list)
    
    def test_add_delete_spot(self):
        testAddSpot = db.add_spot(None, None, None, None, None)
        print(f"{testAddSpot=}")
        self.assertIsInstance(testAddSpot, str)
        testDeleteSpot = db.delete_spot(testAddSpot)
        self.assertIsInstance(testDeleteSpot, DeleteResult)
    
    def test_update_spot(self):
        testUpdateSpot = db.update_spot(self.spot_id, "TEST UPDATE SPOT", None, None, None, None)
        self.assertIsInstance(testUpdateSpot, UpdateResult)
        testUpdateSpot = db.get_spot_detail(self.spot_id)
        self.assertEqual(testUpdateSpot["spotName"], "TEST UPDATE SPOT")
    
    def test_get_spot_detail(self):
        testGetSpotDetail = db.get_spot_detail(self.spot_id)
        self.assertIsInstance(testGetSpotDetail, dict)
    
    def test_update_factors(self):
        updatedFactors = {
            "factorAvailability": 0,
            "factorNoiseLevel": 0,
            "factorTemperature": 0,
            "factorAmbiance": 0
        }
        testUpdateFactors = db.update_spot_factors(self.spot_id, updatedFactors)
        self.assertEqual(str(testUpdateFactors), self.spot_id)
    
    def test_get_avergage(self):
        avg = db.get_average(0, 1, 5)
        self.assertEqual(avg, 2.5)
    
    def test_add_delete_review(self):
        testAddReview = db.add_review(self.spot_id, None, None, None, "abcd")
        self.assertIsInstance(testAddReview, str)
        testDeleteReview = db.delete_review(testAddReview, "abcd", False)
        self.assertIsInstance(testDeleteReview, DeleteResult)

    def test_update_review(self):
        testUpdateReview = db.update_review(self.review_id, self.spot_id, None, None, None, "abcde")
        self.assertIsInstance(testUpdateReview, UpdateResult)
        testUpdateReview = db.get_review_by_spot(self.spot_id)
        self.assertIsInstance(testUpdateReview, list)
        self.assertIsNone(testUpdateReview[0]["reviewTitle"])
    
    def test_get_file(self):
        fileID = dbc.save_file("fakefile", BytesIO(b"abcde"))
        file = db.get_file(str(fileID))
        self.assertIsInstance(file, tuple)
        self.assertIsInstance(file[0], BytesIO)
        self.assertIsInstance(file[1], str)