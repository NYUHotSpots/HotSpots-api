"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

from http import HTTPStatus
from flask import Flask
from flask_restx import Resource, Api, reqparse
import werkzeug.exceptions as wz

import db.data as db

app = Flask(__name__)
api = Api(app)

flavorParser = reqparse.RequestParser()
flavorParser.add_argument('flavorName', type=str, location='form')
flavorParser.add_argument('flavorImage', type=str, location='form')
flavorParser.add_argument('flavorDescription', type=str, location='form')
flavorParser.add_argument('flavorNutrition', type=str, location='form')
flavorParser.add_argument('flavorPrice', type=int, location='form')
flavorParser.add_argument('flavorAvailability', type=bool, location='form')

reviewParser = reqparse.RequestParser()
reviewParser.add_argument('reviewName', type=str, location='form')
reviewParser.add_argument('flavorID', type=str, location='form')
reviewParser.add_argument('reviewText', type=str, location='form')


@api.route('/hello')
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        It just answers with "hello world."
        """
        return {"Hola": "Mundo"}


@api.route('/flavors')
class Flavor(Resource):
    """
    This endpoint returns a list of all flavors
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        """
        Returns a dictionary of all flavors
        """
        flavors = db.get_flavors()
        if flavors is None:
            raise (wz.NotFound("Flavors not found."))
        else:
            return flavors

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    @api.doc(parser=flavorParser)
    def post(self):
        """
        Creates a new flavor
        """
        args = flavorParser.parse_args()
        flavor_entry = buildFlavorObject(args['flavorName'],
                                         args['flavorImage'],
                                         args['flavorDescription'],
                                         args['flavorNutrition'],
                                         args['flavorPrice'],
                                         args['flavorAvailability'])
        flavor_response = db.add_flavor(flavor_entry)
        if flavor_response == db.DUPLICATE:
            raise (wz.NotAcceptable("Flavor already exists."))
        else:
            return flavor_response


@api.route('/flavors/<flavor_id>')
class FlavorDetail(Resource):
    """
    This endpoint returns a details of a flavor
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, flavor_id):
        """
        Returns a details of a flavor
        """
        flavor_detail = db.get_flavor_detail(flavor_id)
        if flavor_detail == db.NOT_FOUND:
            raise (wz.NotFound("Flavor detail not found."))
        else:
            return flavor_detail

    """
    This endpoint updates a flavor
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.doc(parser=flavorParser)
    def put(self, flavor_id):
        """
        Update a flavor
        """
        args = flavorParser.parse_args()
        flavor_update = buildFlavorObject(args['flavorName'],
                                          args['flavorImage'],
                                          args['flavorDescription'],
                                          args['flavorNutrition'],
                                          args['flavorPrice'],
                                          args['flavorAvailability'])
        flavor_response = db.update_flavor(flavor_id, flavor_update)
        if flavor_response == db.NOT_FOUND:
            raise (wz.NotFound("Flavor not found."))
        else:
            return f"{flavor_response} added."

    """
    This endpoint deletes a new flavor
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def delete(self, flavor_id):
        """
        Delete a flavor
        """
        flavor_response = db.delete_flavor(flavor_id)
        if flavor_response == db.NOT_FOUND:
            raise (wz.NotFound("Flavor not found."))
        else:
            return f"{flavor_response} deleted."


@api.route('/reviews')
class Review(Resource):
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    @api.doc(parser=reviewParser)
    def post(self):
        """
        Creates a new review
        """
        args = reviewParser.parse_args()
        review_response = db.add_review(args['reviewName'],
                                        args['flavorID'],
                                        args['reviewText'])
        if review_response == db.DUPLICATE:
            raise (wz.NotAcceptable("Flavor already exists."))
        else:
            return f"{review_response} added."


def buildFlavorObject(name, image, description, nutrition,
                      price, availability, id=None):
    flavor_object = {
        "flavorName": name,
        "flavorImage": image,
        "flavorDescription": description,
        "flavorNutrition": nutrition,
        "flavorPrice": price,
        "flavorAvailability": availability
    }
    return flavor_object
