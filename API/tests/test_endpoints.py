"""
This file holds the tests for endpoints.py.
"""

from unittest import TestCase, skip 
from flask_restx import Resource, Api

import API.endpoints as ep
import db.data as db

class EndpointTestCase(TestCase):
    def setUp(self):
        self.app = ep.app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.flavorData = {
            "flavorName": "TEST FLAVOR",
            "flavorImage": "WWW.GOOGLE.COM",
            "flavorDescription": "TEST DESCRIPTION",
            "flavorNutrition": "TEST NUTRITION",
            "flavorPrice": 1,
            "flavorAvailability": True
        }
        self.updatedFlavorData = {
            "flavorName": "UPDATE TEST FLAVOR",
            "flavorImage": "UPDATE WWW.GOOGLE.COM",
            "flavorDescription": "UPDATE DESCRIPTION",
            "flavorNutrition": "UPDATE NUTRITION",
            "flavorPrice": 2,
            "flavorAvailability": False
        }
        self.reviewData = {
            "reviewName": "TEST REVIEW",
            "flavorID": "123",
            "reviewText": "TEST TEXT"
        }

    def tearDown(self):
        print("Tear Down")

    def test_hello(self):
        response = self.client.get("/hello")
        print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_get_flavor(self):
        response = self.client.get("/flavors")
        print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_create_update_delete_flavor(self):
        response = self.client.post("/flavors", data=self.flavorData)
        print(response.data)
        id = response.data.decode("utf-8").strip().strip("\"")
        print("Test Create Flavor", id)
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f"/flavors/{id}")
        print("Test Get Flavor", response.data)
        self.assertEqual(response.status_code, 200)

        response = self.client.put(f"/flavors/{id}", data=self.updatedFlavorData)
        print("Test Update Flavor", response.data)
        self.assertEqual(response.status_code, 200)

        response = self.client.delete(f"/flavors/{id}")
        print("Test Delete Flavor", response.data)
        self.assertEqual(response.status_code, 200)

    def test_create_review(self):
        response = self.client.post("/reviews", data=self.reviewData)
        print("Test Create Review", response)
        self.assertEqual(response.status_code, 200)
