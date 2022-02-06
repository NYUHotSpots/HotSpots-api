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

spotParser = reqparse.RequestParser()
spotParser.add_argument('spotName', type=str, location='form')
spotParser.add_argument('spotImage', type=str, location='form')
spotParser.add_argument('spotAddress', type=str, location='form')
spotParser.add_argument('spotCapacity', type=str, location='form')

reviewParser = reqparse.RequestParser()
reviewParser.add_argument('spotID', type=str, location='form')
reviewParser.add_argument('reviewTitle', type=str, location='form')
reviewParser.add_argument('reviewText', type=str, location='form')
reviewParser.add_argument('reviewRating', type=int, location='form')

factorParser = reqparse.RequestParser() # each will be a number from 1 to 10
factorParser.add_argument('factorAvailability', type=int, location='form')
factorParser.add_argument('factorNoiseLevel', type=int, location='form')
factorParser.add_argument('factorTemperature', type=int, location='form')
factorParser.add_argument('factorAmbiance', type=int, location='form')


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


@api.route('/spot')
class Spot(Resource):
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self):
        """
        Returns all spots
        """
        spots = db.get_spots()
        if spots is None:
            raise (wz.NotFound("Spots not found."))
        else:
            return spots

    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    @api.doc(parser=spotParser)
    def post(self):
        """
        Creates a new spot
        """
        args = spotParser.parse_args()
        spot_response = db.add_spot(args['spotName'], args['spotAddress'],
                                    args['spotCapacity'], args['spotImage'])
        if spot_response == db.DUPLICATE:
            raise (wz.NotAcceptable("Spot already exists."))
        else:
            return spot_response


@api.route('/spot/<spot_id>')
class SpotDetail(Resource):
    """
    This endpoint returns a details of a spot
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, spot_id):
        """
        Returns a details of a spot
        """
        spot_details = db.get_spot_detail(spot_id)
        if spot_details == db.NOT_FOUND:
            raise (wz.NotFound("Spot detail not found."))
        else:
            return spot_details

    """
    This endpoint updates a spot
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.doc(parser=spotParser)
    def put(self, spot_id):
        """
        Update a spot
        """
        args = spotParser.parse_args()
        spot_response = db.update_spot(spot_id, args['spotName'],
                                       args['spotAddress'],
                                       args['spotCapacity'],
                                       args['spotImage'])
        if spot_response == db.NOT_FOUND:
            raise (wz.NotFound("Spot not found."))
        else:
            return f"{spot_response} added."

    """
    This endpoint deletes a new spot
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def delete(self, spot_id):
        """
        Delete a spot
        """
        spot_response = db.delete_spot(spot_id)
        if spot_response == db.NOT_FOUND:
            raise (wz.NotFound("Spot not found."))
        else:
            return f"{spot_response} deleted."


@api.route('/spot/factor/<spot_id>')
class SpotUpdateFactor(Resource):
    """
    This endpoint updates a spot
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.doc(parser=factorParser)
    def put(self, spot_id):
        """
        Update a spot factor
        """
        args = factorParser.parse_args()
        spot_response = db.update_spot_factors(spot_id, args)
        if spot_response == db.NOT_FOUND:
            raise (wz.NotFound("Spot not found."))
        else:
            return f"{spot_response} factor updated."


@api.route('/review')
class Review(Resource):
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    @api.doc(parser=reviewParser)
    def post(self):
        """
        Creates a new review
        """
        args = reviewParser.parse_args()
        review_response = db.add_review(args["spotID"],
                                        args['reviewDate'],
                                        args['reviewTitle'],
                                        args['reviewText'],
                                        args['reviewRating'])
        if review_response == db.DUPLICATE:
            raise (wz.NotAcceptable("Review already exists."))
        else:
            return review_response


@api.route('/review/<review_id>')
class ReviewDetail(Resource):
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def delete(self, review_id):
        """
        Deletes a new review
        """
        review_response = db.delete_review(review_id)
        if review_response == db.NOT_FOUND:
            raise (wz.NotFound("Review not found."))
        else:
            return f"{review_response} deleted."
