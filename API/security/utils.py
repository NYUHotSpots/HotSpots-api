from flask import jsonify, abort, Response
from json import dumps
import os
from dotenv import load_dotenv

load_dotenv()


def json_abort(status_code, message=None):
    if not message:
        message = "There was an error"
    abort(status_code, description=message)


path = os.environ.get("HOTSPOTS_PATH")
audience = os.environ.get("AUTH0_API_AUDIENCE")
domain = os.environ.get("AUTH0_DOMAIN")
