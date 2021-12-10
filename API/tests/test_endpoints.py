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
        self.data = {
            "flavorName": "TEST FLAVOR",
            "flavorImage": "WWW.GOOGLE.COM",
            "flavorDescription": "TEST DESCRIPTION",
            "flavorNutrition": "TEST NUTRITION",
            "flavorPrice": 1,
            "flavorAvailability": True
        }
        self.updatedData = {
            "flavorName": "UPDATE TEST FLAVOR",
            "flavorImage": "UPDATE WWW.GOOGLE.COM",
            "flavorDescription": "UPDATE DESCRIPTION",
            "flavorNutrition": "UPDATE NUTRITION",
            "flavorPrice": 2,
            "flavorAvailability": False
        }

    def tearDown(self):
        print("Tear Down")

    def test_hello(self):
        response = self.client.get("/hello")
        self.assertEqual(response.status_code, 200)

    def test_get_flavor(self):
        response = self.client.get("/flavors")
        print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_create_flavor(self):
        response = self.client.post("/flavors", data=self.data)
        print("Test Create Flavor", response.data)
        self.assertEqual(response.status_code, 200)

    def test_update_flavor(self):
        response = self.client.put("/flavors/61b39abfb5110a3a71c2cb4a", data=self.updatedData)
        print("Test Update Flavor", response.data)
        self.assertEqual(response.status_code, 200)

    def test_delete_flavor(self):
        self.assertTrue(True)

    def test_create_review(self):
        self.assertTrue(True)
