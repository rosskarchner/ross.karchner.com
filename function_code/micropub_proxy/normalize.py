import base64
import email
import json
import io
import os

import requests

from urllib.parse import parse_qsl
from itertools import zip_longest


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
        if isinstance(key, bytes):
            key = key.decode("utf-8")
        if isinstance(value, bytes):
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

    if 'photo' in properties and 'mp-photo-alt' in properties:
        merged_photos = []
        for photo, alt_txt in zip_longest(properties['photo'], properties['mp-photo-alt']):
            merged_photos.append({'value': photo, 'alt':alt_txt})
        properties['photo'] = merged_photos

    return document, access_token


def upload_media(part, access_token):
    media_endpoint = os.environ['MICROPUB_MEDIA']
    filename = part.get_filename()
    fileobj = io.BytesIO(part.get_payload(decode=True))
    content_type = part.get_content_type()
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.post(media_endpoint, files={'file': (filename, fileobj, content_type)}, headers=headers)
    response.raise_for_status()
    return response.headers['location']





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

    elif headers["content-type"].startswith("application/x-www-form-urlencoded"):
        # indigineous (Android) includes charset=UTF-8 in the content type.
        # it might be worth doing something intelligent with that
        parsed_body = parse_qsl(body)
        json_document, body_access_token = kvpairs_to_mfjson(parsed_body)


    elif headers["content-type"].startswith("multipart/form-data"):
        content_type = headers["content-type"]
        body_with_content_type = (
            b"Content-Type: " + content_type.encode() + b"\r\n" + body
        )
        msg = email.parser.BytesParser().parsebytes(body_with_content_type)

        kvpairs_no_files = [(part.get_param('name', header='content-disposition'), part.get_payload()) for part in msg.get_payload() if not part.get_filename()]

        body_access_token = dict(kvpairs_no_files).get('access_token')
        files = ((part.get_param('name', header='content-disposition'), upload_media(part, header_access_token or body_access_token)) for part in msg.get_payload() if part.get_filename())

        # using the existence of files names to determine what is and is not a file may backfire at somepoint

        kvpairs = kvpairs_no_files + list(files)

        json_document, body_access_token = kvpairs_to_mfjson(kvpairs)

        print(json_document)
    return json_document, header_access_token or body_access_token
