"""
This is the file containing all of the endpoints for our flask app.
The endpoint called `endpoints` will return all available endpoints.
"""

from http import HTTPStatus
from flask import Flask, request, jsonify, _request_ctx_stack
from flask_restx import Resource, Api, reqparse
from flask_cors import cross_origin
import werkzeug.exceptions as wz
import json
import os
from six.moves.urllib.request import urlopen
from functools import wraps
from jose import jwt

import db.data as db

app = Flask(__name__)
api = Api(app)

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
API_AUDIENCE = os.environ.get("AUTH0_API_AUDIENCE")
ALGORITHMS = ["RS256"]

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

# each will be a number from 1 to 10
factorParser = reqparse.RequestParser()
factorParser.add_argument('factorAvailability', type=int, location='form')
factorParser.add_argument('factorNoiseLevel', type=int, location='form')
factorParser.add_argument('factorTemperature', type=int, location='form')
factorParser.add_argument('factorAmbiance', type=int, location='form')


# Error handler
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


# Format error response and append status code
def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_auth(f):
    """Determines if the Access Token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer="https://"+AUTH0_DOMAIN+"/"
                )
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    "please check the audience and issuer"}, 401)  # noqa: E501
            except Exception:
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 401)

            _request_ctx_stack.top.current_user = payload
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
    return decorated


def requires_scope(required_scope):
    """Determines if the required scope is present in the Access Token
    Args:
        required_scope (str): The scope required to access the resource
    """
    token = get_token_auth_header()
    unverified_claims = jwt.get_unverified_claims(token)
    if unverified_claims.get("scope"):
        token_scopes = unverified_claims["scope"].split()
        for token_scope in token_scopes:
            if token_scope == required_scope:
                return True
    return False


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
    @cross_origin(headers=["Content-Type", "Authorization"])  # noqa: E501
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
    @cross_origin(headers=["Content-Type", "Authorization"])
    @cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])  # noqa: E501
    @requires_auth
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
    @cross_origin(headers=["Content-Type", "Authorization"])
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
    @cross_origin(headers=["Content-Type", "Authorization"])
    @cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])  # noqa: E501
    @requires_auth
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
    @cross_origin(headers=["Content-Type", "Authorization"])
    @cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])  # noqa: E501
    @requires_auth
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
    @cross_origin(headers=["Content-Type", "Authorization"])
    @cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])  # noqa: E501
    @requires_auth
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
    @cross_origin(headers=["Content-Type", "Authorization"])
    @cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])  # noqa: E501
    @requires_auth
    def post(self):
        """
        Creates a new review
        """
        args = reviewParser.parse_args()
        review_response = db.add_review(args["spotID"],
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
    @cross_origin(headers=["Content-Type", "Authorization"])
    @cross_origin(headers=["Access-Control-Allow-Origin", "http://localhost:3000"])  # noqa: E501
    @requires_auth
    def delete(self, review_id):
        """
        Deletes a new review
        """
        review_response = db.delete_review(review_id)
        if review_response == db.NOT_FOUND:
            raise (wz.NotFound("Review not found."))
        else:
            return f"{review_response} deleted."


@api.route('/review/<spot_id>')
class ReviewSpot(Resource):
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_ACCEPTABLE, 'A duplicate key')
    @cross_origin(headers=["Content-Type", "Authorization"])
    def get(self, spot_id):
        """
        Get review for specific spot
        """
        spot_review_response = db.get_review_by_spot(str(spot_id))
        if spot_review_response == db.NOT_FOUND:
            raise (wz.NotFound("Reviews for spot %s not found.", spot_id))
        else:
            return spot_review_response
