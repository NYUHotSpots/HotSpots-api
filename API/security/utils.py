from flask import abort
import os
import http.client
import json
from dotenv import load_dotenv

load_dotenv()

path = os.environ.get("HOTSPOTS_PATH")
audience = os.environ.get("AUTH0_API_AUDIENCE")
domain = os.environ.get("AUTH0_DOMAIN")
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")


def json_abort(status_code, message=None):
    if not message:
        message = "There was an error"
    abort(status_code, description=message)


def get_auth0_token():
    conn = http.client.HTTPSConnection("hotspots-dev.us.auth0.com")
    payload = {
        "client_id" : client_id, 
        "client_secret" : client_secret, 
        "audience": audience,
        "grant_type": "client_credentials"
    }
    payload = json.dumps(payload)
    headers = { 'content-type': "application/json" }
    conn.request("POST", "/oauth/token", payload, headers)

    res = conn.getresponse()
    data = json.loads(res.read())
    print("New access token: " + data["access_token"])
    return(data["access_token"])