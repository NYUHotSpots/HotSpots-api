"""
This handles user management
Right now (03/04/2022) it's not being used
"""

import http.client
import json
from utils import get_auth0_management_token

conn = http.client.HTTPSConnection("hotspots-dev.us.auth0.com")
bearertoken = "Bearer " + get_auth0_management_token()

headers = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'Authorization': bearertoken
    }

roles_roleID = {"admin": "rol_oOKxNBur6xwV4NUs"}

def create_test_user():
    payload = json.dumps({
        "email": "john1.doe@gmail.com",
        "user_metadata": {},
        "blocked": False,
        "email_verified": False,
        "app_metadata": {},
        "given_name": "John",
        "family_name": "Doe",
        "name": "John Doe",
        "nickname": "Johnny",
        "picture": "https://secure.gravatar.com/avatar/15626c5e0c749cb912f9d1ad48dba440?s=480&r=pg&d=https%3A%2F%2Fssl.gstatic.com%2Fs2%2Fprofiles%2Fimages%2Fsilhouette80.png",
        "user_id": "abc1",
        "connection": "Username-Password-Authentication",
        "password": "Secrets1!",
        "verify_email": False
    })
    conn.request("POST", "/api/v2/users", payload, headers)
    res = json.loads(conn.getresponse().read().decode())
    print("CREATED USERS:")
    print(res)
    print(type(res))
    
def get_users(): 
    conn.request("GET", "/api/v2/users", headers=headers)
    res = json.loads(conn.getresponse().read().decode())
    print(res)

def assign_role_to_user(user_id, role):
    payload = json.dumps({"roles": [role]})
    conn.request("POST", f"api/v2/users/{user_id}/roles", payload, headers)
    res = conn.getresponse().read()
    print(res)
    
def get_users_by_email(email):
    conn.request("GET", f"/api/v2/users-by-email?email={email}", headers=headers)
    res = json.loads(conn.getresponse().read().decode())
    user_id = res[0]["user_id"]
    return user_id
    

test_user_id = get_users_by_email("john1.doe@gmail.com")
get_users()
assign_role_to_user(test_user_id, roles_roleID["admin"])
