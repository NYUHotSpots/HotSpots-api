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
management_audience = os.environ.get("AUTH0_MANAGEMENT_AUDIENCE")


def json_abort(status_code, message=None):
    if not message:
        message = "There was an error"
    abort(status_code, description=message)


def get_auth0_token():
    conn = http.client.HTTPSConnection(domain)
    payload = json.dumps({
        "client_id" : client_id, 
        "client_secret" : client_secret, 
        "audience": audience,
        "grant_type": "client_credentials"
    })
    headers = { 'content-type': "application/json" }
    conn.request("POST", "/oauth/token", payload, headers)

    res = conn.getresponse().read()
    access_token = json.loads(res)["access_token"]
    print("New access token: " + access_token)
    return access_token


def get_auth0_management_token():
    conn = http.client.HTTPSConnection("hotspots-dev.us.auth0.com")
    payload = json.dumps({
        "client_id" : client_id, 
        "client_secret" : client_secret, 
        "audience": management_audience,
        "grant_type": "client_credentials"
    })
    headers = { 'content-type': "application/json" }
    conn.request("POST", "/oauth/token", payload, headers)

    res = conn.getresponse().read()
    access_token = json.loads(res)["access_token"]
    print("New management access token: " + access_token)
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    return access_token


def get_access_token_for_test_user():
    conn = http.client.HTTPSConnection(domain)
    payload = json.dumps({
        "grant_type" : "password",
        "client_id": client_id,
        "client_secret": client_secret,
        "otp": "CODE",
        "realm": "email",
        "username":"john1.doe@gmail.com",
        "password":"Secrets1!",
        "audience" : audience,
        "connection": "Username-Password-Authentication",
        "scope": "openid"
    }) 
    # for scope we can also use openid profile email 
    # if we want profile info
    headers = { 'content-type': "application/json" }
    conn.request("POST", "/oauth/token", payload, headers)

    res = conn.getresponse().read()
    access_token = json.loads(res)["access_token"]
    print("New access token test user: " + access_token)
    return access_token