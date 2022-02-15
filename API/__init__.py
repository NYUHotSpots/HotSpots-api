##########################################
# External Modules
##########################################

import os
from dotenv import load_dotenv

from flask import Flask
from flask_cors import CORS
from flask_talisman import Talisman

from API.security.auth0_service import auth0_service

load_dotenv()


def create_app():
    ##########################################
    # Environment Variables
    ##########################################
    client_origin_url = os.environ.get("CLIENT_ORIGIN_URL")
    auth0_audience = os.environ.get("AUTH0_API_AUDIENCE")
    auth0_domain = os.environ.get("AUTH0_DOMAIN")

    if not (client_origin_url and auth0_audience and auth0_domain):
        raise NameError("The required environment variables are missing. Check .env file.")  # noqa E501

    ##########################################
    # Flask App Instance
    ##########################################

    app = Flask(__name__, instance_relative_config=True)

    ##########################################
    # HTTP Security Headers
    ##########################################

    csp = {
        'default-src': ['\'self\''],
        'frame-ancestors': ['\'none\'']
    }

    Talisman(app,
             frame_options='DENY',
             content_security_policy=csp,
             referrer_policy='no-referrer'
             )

    auth0_service.initialize(auth0_domain, auth0_audience)

    @app.after_request
    def add_headers(response):
        response.headers['X-XSS-Protection'] = '0'
        response.headers['Cache-Control'] = 'no-store, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response

    ##########################################
    # CORS
    ##########################################

    CORS(
        app,
        resources={r"/api/*": {"origins": client_origin_url}},
        allow_headers=["Authorization", "Content-Type"],
        methods=["GET"],
        max_age=86400
    )

    return app
