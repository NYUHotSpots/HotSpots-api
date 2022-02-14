"""
This file holds the tests for endpoints.py.
"""

from email import header
from unittest import TestCase, skip
from urllib import response 
from flask_restx import Resource, Api
import os

import datetime
import API.endpoints as ep
import db.data as db

BEARER_TEST_TOKEN = os.environ.get("BEARER_TEST_TOKEN")
bearer = f"Bearer {BEARER_TEST_TOKEN}"

class EndpointTestCase(TestCase):
    def setUp(self):
        self.app = ep.app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.spotData = {
            "spotName": "TEST SPOT",
            "spotAddress": "6 MetroTech Center, Brooklyn, NY 11201",
            "spotCapacity": "Medium"
        }
        self.updatedSpotData = self.spotData
        self.updatedSpotData["spotCapacity"] = "Low"
        self.reviewData = {
            "spotID": "0",
            "reviewTitle": "test_endpoints_unit_test", 
            "reviewText": "wow what a great app", 
            "reviewRating": "5"
        }
        self.headers = { 'authorization': bearer }

    
    def tearDown(self):
        print("Tear Down")

    def test_hello(self):
        response = self.client.get("/hello", headers=self.headers)
        print(response.data)
        self.assertEqual(response.status_code, 200)
        
    def test_get_all_spots(self):
        response = self.client.get("/spot", headers=self.headers)
        print(response.data)
        self.assertEqual(response.status_code, 200)
        
    def test_create_update_delete_spot(self):
        response = self.client.post("/spot", data=self.spotData, headers=self.headers)
        spot_id = response.data.decode("utf-8").strip().strip("\"")
        print("Test Create Spot", spot_id)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(f"/spot/{spot_id}", headers=self.headers)
        print("Test Get Spot", response.data)
        self.assertEqual(response.status_code, 200)

        response = self.client.put(f"/spot/{spot_id}", data=self.updatedSpotData, headers=self.headers)
        print("Test Update Spot", response.data)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.delete(f"/spot/{spot_id}", headers=self.headers)
        print("Test Delete Spot", response.data)
        self.assertEqual(response.status_code, 200)
        
    def test_create_review(self):
        response = self.client.post("/spot", data=self.spotData, headers=self.headers)
        print(response.data)
        spot_id = response.data.decode("utf-8").strip().strip("\"")
        print("Test Create Review (Make Spot First)", spot_id)
        self.assertEqual(response.status_code, 200)
        
        self.reviewData["spotID"] = spot_id
        response = self.client.post("/review", data=self.reviewData, headers=self.headers)
        review_id = response.data.decode("utf-8").strip().strip("\"")
        print("Test Create Review", review_id)
        print(response.data)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(f"/review/{spot_id}", headers=self.headers)
        print("Test Get Review", response.data)
        self.assertEqual(response.status_code, 200)

        response = self.client.delete(f"/review/{review_id}", headers=self.headers)
        print("Test Delete Review", response.data)
        self.assertEqual(response.status_code, 200)
