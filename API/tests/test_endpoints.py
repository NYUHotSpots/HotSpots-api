"""
This file holds the tests for endpoints.py.
"""

from unittest import TestCase
import API.endpoints as ep
from API.security.utils import get_auth0_token, get_access_token_for_test_user

userToken = "Bearer " + get_access_token_for_test_user() # this gives a token for the test user johndoe1 who has the admin role
# bearer = "Bearer " + get_auth0_token() # this gives a token that doesn't have the permissions set

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
        self.headers = {"authorization": userToken}
        self.bad_id = "000000000000000000000000"
        self.factor_form = {                
            "factorDate": "2022-02-23",
            "factorValue": "4",
            "factorNumOfInputs": "1"
        }
        self.factor = {
            "factorAvailability": self.factor_form,
            "factorNoiseLevel": self.factor_form,
            "factorTemperature": self.factor_form,
            "factorAmbiance": self.factor_form
        }
    
    def tearDown(self):
        print("Tear Down")

    def test_hello(self):
        response = self.client.get("/hello", headers=self.headers)
        print(response.data)
        self.assertEqual(response.status_code, 200)
    
    def test_bad_permissions(self):
        no_permissions_token = "Bearer " + get_auth0_token()
        self.headers["authorization"] = no_permissions_token
        response = self.client.post("/spots/create", data=self.spotData, headers=self.headers)
        print(response.data)
        self.assertEqual(response.status_code, 403)
        
    def test_get_all_spots(self):
        response = self.client.get("/spots/list", headers=self.headers)
        print(response.data)
        self.assertEqual(response.status_code, 200)
        
    def test_spot_crud(self):
        response = self.client.post("/spots/create", data=self.spotData, headers=self.headers)
        spot_id = response.data.decode("utf-8").strip().strip("\"")
        print("Test Create Spot", spot_id)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(f"/spots/{spot_id}", headers=self.headers)
        print("Test Get Spot Detail", response.data)
        self.assertEqual(response.status_code, 200)

        response = self.client.put(f"/spots/update/{spot_id}", data=self.updatedSpotData, headers=self.headers)
        print("Test Update Spot", response.data)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.delete(f"/spots/delete/{spot_id}", headers=self.headers)
        print("Test Delete Spot", response.data)
        self.assertEqual(response.status_code, 200)
        
    def test_review_crud(self):
        response = self.client.post("/spots/create", data=self.spotData, headers=self.headers)
        print(response.data)
        spot_id = response.data.decode("utf-8").strip().strip("\"")
        print("Test Create Review (Make Spot First)", spot_id)
        self.assertEqual(response.status_code, 200)
        
        self.reviewData["spotID"] = spot_id
        response = self.client.post("/spot_review/create", data=self.reviewData, headers=self.headers)
        review_id = response.data.decode("utf-8").strip().strip("\"")
        print("Test Create Review", review_id)
        print(response.data)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(f"/spot_review/read/{spot_id}", headers=self.headers)
        print("Test Get Review", response.data)
        self.assertEqual(response.status_code, 200)
        
        self.reviewData["reviewTitle"] = "test_review_crud"
        response = self.client.put(f"/spot_review/update/{review_id}", data=self.reviewData, headers=self.headers)
        print("Test Update Review", response.data)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(f"/spot_review/read/{spot_id}", headers=self.headers)
        print(response.data)

        response = self.client.delete(f"/spot_review/delete/{review_id}", headers=self.headers)
        print("Test Delete Review", response.data)
        self.assertEqual(response.status_code, 200)
        
    def test_factor_crud(self):
        response = self.client.post("/spots/create", data=self.spotData, headers=self.headers)
        spot_id = response.data.decode("utf-8").strip().strip("\"")
        self.assertEqual(response.status_code, 200)
        
        response = self.client.put(f"/spot_factors/update/{spot_id}", json=self.factor, headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_bad_requests(self):
        response = self.client.post("/spots/create", data=self.spotData)
        self.assertEqual(response.status_code, 401)
        
        bad_header = {"authorization" : "Bearer "}
        response = self.client.post("/spots/create", data=self.spotData, headers=bad_header)
        self.assertEqual(response.status_code, 400)

    def test_bad_deletes(self):
        '''
        This tests poorly formatted IDs (raises bson InvalidId error) 
        and IDs that aren't found in the DB 
        (if you call delete and that doc isn't found, 
        then mongo will just pretend like it did delete it without raising any error)
        '''
        response = self.client.delete(f"/spot_delete/1234", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        
        response = self.client.delete(f"/spot_delete/{self.bad_id}", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        
        response = self.client.delete(f"/spots/delete/1234", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        
        response = self.client.delete(f"/spots/delete/{self.bad_id}", headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_bad_put(self): 
        response = self.client.put(f"/spots/update/{self.bad_id}", data=self.updatedSpotData, headers=self.headers)
        print("Test Bad Spot Put")
        self.assertEqual(response.status_code, 404)
        
        response = self.client.get(f"/spots/{self.bad_id}", headers=self.headers)
        # make sure it wasn't created
        self.assertEqual(response.status_code, 404)

        print("Test Bad Factor Put")
        response = self.client.put(f"/spot_factors/update/{self.bad_id}", json=self.factor, headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_bad_get_by_id(self): 
        response = self.client.get(f"/spots/{self.bad_id}", headers=self.headers)
        print("Test Bad Get Spot Detail", response.data)
        self.assertEqual(response.status_code, 404)
        
        response = self.client.get(f"/spot_read/{self.bad_id}", headers=self.headers)
        print("Test Bad Get Review", response.data)
        self.assertEqual(response.status_code, 404)

    def test_bad_post(self):
        self.reviewData["spotID"] = self.bad_id
        response = self.client.post("/spot_create", data=self.reviewData, headers=self.headers)
        print("Test Bad Create Review", response)
        self.assertEqual(response.status_code, 404)
