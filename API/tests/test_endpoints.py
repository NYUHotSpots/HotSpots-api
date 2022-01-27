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
        self.spotData = {
            "spotName": "TEST SPOT",
            "spotAddress": "6 MetroTech Center, Brooklyn, NY 11201",
            "spotCapacity": "Medium"
        }
        self.updatedSpotData = self.spotData
        self.updatedSpotData["spotCapacity"] = "Low"
    
    def tearDown(self):
        print("Tear Down")

    def test_hello(self):
        response = self.client.get("/hello")
        print(response.data)
        self.assertEqual(response.status_code, 200)
        
    def test_get_all_spots(self):
        response = self.client.get("/spot")
        print(response.data)
        self.assertEqual(response.status_code, 200)
        
    def test_create_update_delete_spot(self):
        response = self.client.post("/spot", data=self.spotData)
        print(response.data)
        spot_id = response.data.decode("utf-8").strip().strip("\"")
        print("Test Create Spot", spot_id)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(f"/spot/{spot_id}")
        print("Test Get Spot", response.data)
        self.assertEqual(response.status_code, 200)

        response = self.client.put(f"/spot/{spot_id}", data=self.updatedSpotData)
        print("Test Update Spot", response.data)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.delete(f"/spot/{spot_id}")
        print("Test Delete Spot", response.data)
        self.assertEqual(response.status_code, 200)