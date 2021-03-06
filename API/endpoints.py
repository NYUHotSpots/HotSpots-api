"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

from http import HTTPStatus
from flask import Flask, g, send_file
from flask_cors import CORS
from flask_restx import Resource, Api
import werkzeug.exceptions as wz

import db.data as db
from API.security.guards import (authorization_guard,
                                 permissions_guard, hotspots_permissions)
from API.parsers import spotParser, factorParser, reviewParser

app = Flask(__name__)

authorizations = {
    'bearerAuth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Type in the *'Value'* input box below: \
            **'Bearer &lt;JWT&gt;'**, where JWT is the token"
    }
}

app.config['ERROR_404_HELP'] = False
CORS(app)
api = Api(app, authorizations=authorizations)
spots_ns = api.namespace("spots", description="adjust spots")
factors_ns = api.namespace("spot_factors",
                           description="adjust factors for spot")
review_ns = api.namespace("spot_review", description="adjust review for spot")
spot_factor_types_ns = api.namespace(
    "spot_factor_types", description="adjust review for spot")  # hateoas


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


@spots_ns.route('/list')
class SpotList(Resource):
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


@spots_ns.route('/create')
class SpotCreate(Resource):
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    @api.doc(parser=spotParser, security='bearerAuth')
    @authorization_guard
    @permissions_guard([hotspots_permissions.admin])
    def post(self):
        """
        Creates a new spot
        """
        args = spotParser.parse_args()
        print(args)
        spot_response = db.add_spot(args['spotName'], args['spotAddress'],
                                    args['spotCapacity'], args['spotImage'],
                                    args['spotImageUpload'])
        if spot_response == db.DUPLICATE:
            raise (wz.NotAcceptable("Spot already exists."))
        else:
            return spot_response


@spots_ns.route('/<spot_id>')
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
            raise (wz.NotFound(f"Spot {spot_id} detail not found."))
        else:
            return spot_details


@spots_ns.route('/update/<spot_id>')
class SpotUpdate(Resource):
    """
    This endpoint updates a spot
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.doc(parser=spotParser, security='bearerAuth')
    @authorization_guard
    @permissions_guard([hotspots_permissions.admin])
    def put(self, spot_id):
        """
        Update a spot
        """
        args = spotParser.parse_args()
        spot_response = db.update_spot(spot_id, args['spotName'],
                                       args['spotAddress'],
                                       args['spotCapacity'],
                                       args['spotImage'],
                                       args['spotImageUpload'])
        if spot_response == db.NOT_FOUND:
            raise (wz.NotFound(f"Spot {spot_id} not found."))
        else:
            return f"{spot_response} added."


@spots_ns.route('/delete/<spot_id>')
class SpotDelete(Resource):
    """
    This endpoint deletes a new spot
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.doc(security='bearerAuth')
    @authorization_guard
    @permissions_guard([hotspots_permissions.admin])
    def delete(self, spot_id):
        """
        Delete a spot
        """
        spot_response = db.delete_spot(spot_id)
        if spot_response == db.NOT_FOUND:
            raise (wz.NotFound(f"Spot {spot_id} not found."))
        else:
            return f"{spot_response} deleted."


@factors_ns.route('/update/<spot_id>')
class SpotUpdateFactor(Resource):
    """
    This endpoint updates spot factors
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.doc(parser=factorParser, security='bearerAuth')
    @authorization_guard
    def put(self, spot_id):
        """
        Update a spot factor
        """
        # args = request.get_json(force=True)
        args = factorParser.parse_args()
        spot_response = db.update_spot_factors(spot_id, args)
        if spot_response == db.NOT_FOUND:
            raise (wz.NotFound(f"Spot {spot_id} not found."))
        else:
            return f"{spot_response} factor updated."


@review_ns.route('/create')
class ReviewCreate(Resource):
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    @api.doc(parser=reviewParser, security='bearerAuth')
    @authorization_guard
    def post(self):
        """
        Creates a new review
        """
        args = reviewParser.parse_args()
        review_response = db.add_review(args["spotID"],
                                        args['reviewTitle'],
                                        args['reviewText'],
                                        args['reviewRating'],
                                        g.user_id)
        if review_response == db.DUPLICATE:
            raise (wz.NotAcceptable("Review already exists."))
        elif review_response == db.NOT_FOUND:
            spotID = args["spotID"]
            raise (wz.NotFound(f"Spot {spotID} doesn't exist"))
        else:
            print("ReviewCreate", review_response)
            return review_response


@review_ns.route('/delete/<review_id>')
class ReviewDelete(Resource):
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    @api.response(HTTPStatus.NOT_FOUND, 'Review not found')
    @api.doc(security='bearerAuth')
    @authorization_guard
    def delete(self, review_id):
        """
        Deletes a new review
        """
        if hotspots_permissions.admin in g.permissions:
            admin = True
        else:
            admin = False
        review_response = db.delete_review(review_id, g.user_id, admin)
        if review_response == db.NOT_FOUND:
            raise (wz.NotFound(f"Review {review_id} not found."))
        else:
            return f"{review_response} deleted."


@review_ns.route('/read/<spot_id>')
class ReviewSpot(Resource):
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    def get(self, spot_id):
        """
        Get review for specific spot
        """
        spot_review_response = db.get_review_by_spot(str(spot_id))
        if spot_review_response == db.NOT_FOUND:
            raise (wz.NotFound(f"Reviews for spot {spot_id} not found."))
        else:
            return spot_review_response


@review_ns.route('/update/<review_id>')
class ReviewUpdate(Resource):
    """
    This endpoint updates a review
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    @api.doc(parser=reviewParser, security='bearerAuth')
    @authorization_guard
    def put(self, review_id):
        """
        Update a review
        """
        args = reviewParser.parse_args()
        review_response = db.update_review(review_id,
                                           args["spotID"],
                                           args['reviewTitle'],
                                           args['reviewText'],
                                           args['reviewRating'],
                                           g.user_id)
        if review_response == db.NOT_FOUND:
            raise (wz.NotFound(f"Spot {review_id} not found."))
        else:
            return f"{review_response} factor updated."


@api.route('/file/<file_id>')
class File(Resource):
    def get(self, file_id):
        response = db.get_file(file_id)
        print(response)
        if response == db.NOT_FOUND:
            raise (wz.NotFound(f"File {file_id} not found."))
        return send_file(response[0], attachment_filename=response[1])


@spot_factor_types_ns.route('/get')
class HATEOASSpotFactors(Resource):
    """
    This endpoint returns a pick list of spot factors
    """
    @api.response(HTTPStatus.OK, 'Success')
    def get(self):
        """
        Return Spot factors
        """
        factors = {
            "availability": {
                "display_name": "Availability",
                "pick_list": [
                    ("At capacity (No seats)", 1),
                    ("Crowded (limited seating)", 2),
                    ("Not too crowded (Some seats available)", 3),
                    ("Many seats", 4),
                    ("Too many seats free", 5)
                ]
            },
            "noise": {
                "display_name": "Noise Level",
                "pick_list": [
                    ("Quiet (silent / near silent)", 1),
                    ("Some noise (whispering to normal speech)", 2),
                    ("Noisy (very loud)", 3),
                    ("Unbearably loud", 4),
                    ("Ruptured eardrum", 5)
                ]
            },
            "temp": {
                "display_name": "Temperature",
                "pick_list": [
                    ("Cold / Chilly", 1),
                    ("Comfortable", 2),
                    ("Warm / Hot", 3),
                    ("Flaming", 4),
                    ("Burning", 5)
                ]
            },
            "ambi": {
                "display_name": "Ambiance",
                "pick_list": [
                    ("Chill", 1),
                    ("Regular", 2),
                    ("Neutral", 3),
                    ("Busy", 4),
                    ("Serious/Business", 5)
                ]
            }
        }
        return factors
