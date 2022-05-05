"""
This file holds the tests for endpoints.py.
"""

from unittest import TestCase
import API.endpoints as ep
import json
from io import BytesIO
from API.security.utils import get_auth0_token, get_access_token_for_test_user

userToken = "Bearer " + get_access_token_for_test_user() # this gives a token for the test user johndoe1 who has the admin role
# bearer = "Bearer " + get_auth0_token() # this gives a token that doesn't have the permissions set
no_permissions_token = "Bearer " + get_auth0_token()

class EndpointTestCase(TestCase):
    def setUp(self):
        self.app = ep.app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.spotData = {
            "spotName": "TEST SPOT",
            "spotAddress": "6 MetroTech Center, Brooklyn, NY 11201",
            "spotImage": "Nothing",
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
        self.bad_headers = {"authorization": no_permissions_token}
        self.bad_id = "000000000000000000000000"
        self.factor = {
            "factorAvailability": "1",
            "factorNoiseLevel": "2",
            "factorTemperature": "3",
            "factorAmbiance": "4"
        }
        self.delete_ids = {"spot":[], "review":[]}
    
    def proper_spot_structure(self, spotDetail):
        fields = ["_id"] + list(self.spotData.keys()) + list(self.factor.keys())
        self.structure_test(fields, spotDetail)
    
    def proper_review_structure(self, reviewDetail):
        fields = self.reviewData.keys()
        self.structure_test(fields, reviewDetail)
    
    def structure_test(self, fields, detail):
        for field in fields:
            self.assertIn(field, detail)
    
    def tearDown(self):
        print("Tear Down")
        print(self.delete_ids)
        for id in self.delete_ids["spot"]:
            self.client.delete(f"/spots/delete/{id}", headers=self.headers)
        for id in self.delete_ids["review"]:
            self.client.delete(f"/spot_review/delete/{id}", headers=self.headers)

    def test_hello(self):
        response = self.client.get("/hello", headers=self.headers)
        print(response.data)
        self.assertEqual(response.status_code, 200)
    
    def test_bad_permissions(self):
        response = self.client.post("/spots/create", data=self.spotData, headers=self.bad_headers)
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
        spotDetail = json.loads(response.data.decode("utf-8"))
        self.proper_spot_structure(spotDetail)

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
        self.delete_ids["spot"].append(spot_id)
        
        self.reviewData["spotID"] = spot_id
        response = self.client.post("/spot_review/create", data=self.reviewData, headers=self.headers)
        review_id = response.data.decode("utf-8").strip().strip("\"")
        print("Test Create Review", review_id)
        print(response.data)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(f"/spot_review/read/{spot_id}", headers=self.headers)
        print("Test Get Review", response.data)
        self.assertEqual(response.status_code, 200)
        reviewDetail = json.loads(response.data.decode("utf-8"))[0]
        self.proper_review_structure(reviewDetail)

        self.reviewData["reviewTitle"] = "test_review_crud"
        response = self.client.put(f"/spot_review/update/{review_id}", data=self.reviewData, headers=self.headers)
        print("Test Update Review", response.data)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(f"/spot_review/read/{spot_id}", headers=self.headers)
        reviews = json.loads(response.data.decode("utf-8"))
        for review in reviews: 
            # since it returns a list, we need the find the updated one
            if (review["_id"]["$oid"] == review_id):
                self.assertEqual(review["reviewTitle"], "test_review_crud")
                break
         
        response = self.client.delete(f"/spot_review/delete/{review_id}", headers=self.headers)
        print("Test Delete Review", response.data)
        self.assertEqual(response.status_code, 200)
        
    def test_factor_crud(self):
        response = self.client.post("/spots/create", data=self.spotData, headers=self.headers)
        spot_id = response.data.decode("utf-8").strip().strip("\"")
        self.assertEqual(response.status_code, 200)
        self.delete_ids["spot"].append(spot_id)
        
        response = self.client.put(f"/spot_factors/update/{spot_id}", data=self.factor, headers=self.headers)
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
        response = self.client.put(f"/spot_factors/update/{self.bad_id}", data=self.factor, headers=self.headers)
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

    def test_bad_user_update_delete_review(self):
        response = self.client.post("/spots/create", data=self.spotData, headers=self.headers)
        print(response.data)
        spot_id = response.data.decode("utf-8").strip().strip("\"")
        print("Test Bad Review (Make Spot First)", spot_id)
        self.assertEqual(response.status_code, 200)
        self.delete_ids["spot"].append(spot_id)
        
        self.reviewData["spotID"] = spot_id
        response = self.client.post("/spot_review/create", data=self.reviewData, headers=self.headers)
        review_id = response.data.decode("utf-8").strip().strip("\"")
        print("Test Bad Review (Make Review First)", review_id)
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.delete_ids["review"].append(review_id)
        
        response = self.client.put(f"/spot_review/update/{review_id}", data=self.reviewData, headers=self.bad_headers)
        print("Test Update Wrong User", response.data)
        self.assertEqual(response.status_code, 403)
        
        response = self.client.delete(f"/spot_review/delete/{review_id}", headers=self.bad_headers)
        print("Test Delete Wrong User", response.data)
        self.assertEqual(response.status_code, 403)

    def test_image_crud(self):
        self.spotData['spotImageUpload'] = (BytesIO(b"abcdef"), 'test.jpg')
        self.headers["content_type"] = 'multipart/form-data'
        response = self.client.post("/spots/create", data=self.spotData, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        spot_id = response.data.decode("utf-8").strip().strip("\"")
        
        response = self.client.get(f"/spots/{spot_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        spotImage = json.loads(response.data.decode("utf-8"))["spotImage"]
        print(f"{spotImage=}")
        
        response = self.client.get(spotImage)
        self.assertEqual(response.status_code, 200)
        print(response)
        
        self.spotData['spotImageUpload'] = (BytesIO(b"abcdefg"), 'test1.jpg')
        response = self.client.put(f"/spots/update/{spot_id}", data=self.spotData, headers=self.headers)
        print("Test Update Spot", response.data)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(f"/spots/{spot_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        spotImage2 = json.loads(response.data.decode("utf-8"))["spotImage"]
        self.assertNotEqual(spotImage, spotImage2)
        
        response = self.client.get(spotImage)
        self.assertEqual(response.status_code, 404)
        print(response)
        
        response = self.client.delete(f"/spots/delete/{spot_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(spotImage2)
        self.assertEqual(response.status_code, 404)
        print(response)