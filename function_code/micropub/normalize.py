import email
import json
import base64
import os
from urllib.parse import parse_qsl, urljoin
import multidict


def kvpairs_to_mfjson(kvpairs):
    types = set(["h-entry"])
    action = None
    url = None
    properties = {}
    access_token = None
    files = {}

    print(kvpairs)
    for key, value in kvpairs:
        print(key)
        if type(key) == bytes:
            key = key.decode("utf-8")
        print(key)
        if type(value) == bytes:
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
                properties[key_no_brackets]=[value,]
        else:
            properties[key] = [value]

    if action and url:
        assert action in ["delete", "undelete"]
        document = {"action": action, "url": url}

    else:
        document = {"type": list(types), "properties": properties}

    return document, access_token


def normalize_micropub_post(event, headers):

    header_access_token = None
    body_access_token = None

    files = {}

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
        print("URL encoded post")
        # print(parsed_body)
        json_document, body_access_token = kvpairs_to_mfjson(parsed_body)

    elif headers["content-type"].startswith("multipart/form-data"):
        content_type = event["headers"]["content-type"]
        body_with_content_type = (
            b"Content-Type: " + content_type.encode() + b"\r\n" + body
        )
        msg = email.parser.BytesParser().parsebytes(body_with_content_type)
        kvpairs = [
            (
                part.get_param("name", header="content-disposition"),
                part.get_payload(decode=False),
            )
            for part in msg.get_payload()
            if not part.get_param("filename", header="content-disposition")
        ]

        files = {
            part.get_param("filename", header="content-disposition"): part.get_payload(
                decode=False
            )
            for part in msg.get_payload()
            if part.get_param("filename", header="content-disposition")
        }
        json_document, body_access_token = kvpairs_to_mfjson(kvpairs)

    return json_document, header_access_token or body_access_token, files
