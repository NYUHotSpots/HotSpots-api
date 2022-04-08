"""
This file holds the tests for db.py.
"""

from unittest import TestCase, skip
import db.data as db

class DBTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

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
        reviews = db.get_review_by_spot("6250aa71bc5ef4d755bdc3c2")
        self.assertIsInstance(reviews, list)