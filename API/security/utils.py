from flask import jsonify, abort
import os
from dotenv import load_dotenv

load_dotenv()


def json_abort(status_code, data=None):
    response = jsonify(data)
    response.status_code = status_code
    abort(response)


path = os.environ.get("HOTSPOTS_PATH")
audience = os.environ.get("AUTH0_API_AUDIENCE")
domain = os.environ.get("AUTH0_DOMAIN")
