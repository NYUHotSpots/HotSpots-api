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
class GetFlavors(Resource):
    """
    This endpoint returns a list of all flavors
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        """
        Returns a list of all flavors
        """
        flavors = db.get_flavors()
        if flavors is None:
            raise (wz.NotFound("Flavors not found."))
        else:
            return flavors


@api.route('/flavors/<flavor_id>')
class GetFlavorDetail(Resource):
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

    def delete(self, flavor_id):
        pass


@api.route('/flavors/create')
class CreateFlavor(Resource):
    """
    This endpoint creates a new flavor
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    @api.doc(parser=flavorParser)
    def post(self):
        """
        Creates a new flavor
        """
        args = flavorParser.parse_args()
        flavor_response = db.add_flavor(args['flavorName'], args['flavorImage'], args['flavorDescription'], args['flavorNutrition'], args['flavorPrice'], args['flavorAvailability'])
        if flavor_response == db.NOT_FOUND:
            raise (wz.NotFound("Flavor not found."))
        elif flavor_response == db.DUPLICATE:
            raise (wz.NotAcceptable("Flavor already exists."))
        else:
            return f"{flavor_response} added."

@api.route('/flavors/update/<flavor_id>')
class UpdateFlavor(Resource):
    """
    This endpoint updates a flavor
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.doc(parser=flavorParser)
    def post(self, flavor_id):
        """
        Update a flavor
        """
        args = flavorParser.parse_args()
        flavor_response = db.update_flavor(flavor_id, args['flavorName'], args['flavorImage'], args['flavorDescription'], args['flavorNutrition'], args['flavorPrice'], args['flavorAvailability'])
        if flavor_response == db.NOT_FOUND:
            raise (wz.NotFound("Flavor not found."))
        else:
            return f"{flavor_response} added."

@api.route('/flavors/delete/<flavor_id>')
class UpdateFlavor(Resource):
    """
    This endpoint deletes a new flavor
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, flavor_id):
        """
        Update a flavor
        """
        flavor_response = db.delete_flavor(flavor_id)
        if flavor_response == db.NOT_FOUND:
            raise (wz.NotFound("Flavor not found."))
        else:
            return f"{flavor_response} deleted."
