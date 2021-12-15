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

    def test_get_flavors(self):
        """
        Can we fetch user db?
        """
        flavors = db.get_flavors()
        self.assertIsInstance(flavors, dict)

