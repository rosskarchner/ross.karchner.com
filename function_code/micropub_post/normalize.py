import base64
import json
from urllib.parse import parse_qsl


def kvpairs_to_mfjson(kvpairs):
    """
    Take a set of key-value pairs from an incoming post, and build a microformats2
    JSON structure.
    """
    types = set(["h-entry"])
    action = None
    url = None
    properties = {}
    access_token = None

    for key, value in kvpairs:
        if isinstance(key,bytes):
            key = key.decode("utf-8")
        if isinstance(value,bytes):
            value = value.decode("utf-8")

        if key == "h":
            types.add("h-" + value)

        elif key == "url":
            url = value

        elif key == "action":
            action = value

        elif key == "access_token":
            access_token = value

        elif key.endswith("[]"):
            key_no_brackets = key[:-2]
            if key_no_brackets in properties:
                properties[key_no_brackets].append(value)
            else:
                properties[key_no_brackets] = [
                    value,
                ]
        else:
            properties[key] = [value]

    if action and url:
        assert action in ["delete", "undelete"]
        document = {"action": action, "url": url}

    else:
        document = {"type": list(types), "properties": properties}

    return document, access_token


def normalize_micropub_post(event, headers):
    """
    Take an incoming AWS Gateway event, which could be base64 encoded,
    could be json, or could be form encoded, and return a microformats2
    json structure, and an access code.
    """

    header_access_token = None
    body_access_token = None

    if "Authorization" in headers:
        header_access_token = headers["Authorization"][7:]

    if event.get("isBase64Encoded"):
        body = base64.b64decode(event["body"])
    else:
        body = event["body"]

    if headers["content-type"] == "application/json":
        json_document = json.loads(event["body"])

    elif headers["content-type"] == "application/x-www-form-urlencoded":
        parsed_body = parse_qsl(body)
        json_document, body_access_token = kvpairs_to_mfjson(parsed_body)

    return json_document, header_access_token or body_access_token
