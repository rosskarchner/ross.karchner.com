import os
from urllib.parse import parse_qsl

import requests

import multidict


def scopes_for_token(token):
    endpoint = os.environ["TOKEN_ENDPOINT"]
    me = os.environ["ME_URL"]

    headers = {"Authorization": "Bearer " + token}
    response = requests.get(endpoint, headers=headers)

    scopes = []

    if response.status_code == 200:
        if response.headers["Content-type"] == "application/x-www-form-urlencoded":
            token_data = multidict.MultiDict(parse_qsl(response.text))

        else:
            token_data = response.json()

        if token_data["me"] == me:
            return token_data.get("scope").split()

    return scopes
