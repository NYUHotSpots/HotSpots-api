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
    
    def tearDown(self):
        print("Tear Down")

    def test_hello(self):
        response = self.client.get("/hello")
        print(response.data)
        self.assertEqual(response.status_code, 200)