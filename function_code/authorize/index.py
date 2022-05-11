import os
from urllib.parse import parse_qsl

import multidict
import requests


def lambda_handler(event, context):
    """
    Take a token, test it against the configured TOKEN_ENDPOINT
    and return a bool indicating whether it's valid, and a list
    of scopes
    """
    print(event)
    endpoint = os.environ["UPSTREAM_TOKEN_ENDPOINT"]
    me = os.environ["ME_URL"]

    authorization_header = event['identitySource'][0]

    headers = {"Authorization": authorization_header, "Accept": "application/json"}
    response = requests.get(endpoint, headers=headers)

    scopes = []
    valid = False

    if response.status_code == 200:
        if response.headers["Content-type"] == "application/x-www-form-urlencoded":
            token_data = multidict.MultiDict(parse_qsl(response.text))

        else:
            token_data = response.json()

        if token_data["me"] == me:
            scopes = token_data.get("scope").split()
            valid = True

    #return valid, scopes
    if valid and scopes:
         return {"isAuthorized": True, 
         "context": {'scopes': scopes}}       
    else:
        return {"isAuthorized": False}