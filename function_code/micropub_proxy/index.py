import os
import requests
import multidict


from normalize import normalize_micropub_post


def lambda_handler(event, context):
    """
    interpret and act on incoming micropub post
    """
    headers = multidict.CIMultiDict(event["headers"])
    allowed_content_types = ["application/json", "application/x-www-form-urlencoded","multipart/form-data"]
    is_allowed_type = False
    for content_type in allowed_content_types:
        if headers.get("content-type").startswith(content_type):
            is_allowed_type = True

    if not is_allowed_type:
        return {"statusCode": 415, "body": "unknown content-type"}

    if event["body"] == "":
        return {"statusCode": 400, "body": "missing body"}

    json_document, access_token = normalize_micropub_post(event, headers=headers)

    if not access_token:
        return {"statusCode": 403, "body": "no access token found"}

    upstream_api = os.environ["MICROPUB_CLEAN"]
    upstream_response = requests.post(
        upstream_api,
        json=json_document,
        headers={"Authorization": "Bearer " + access_token},
    )

    header_whitelist = ['location'] # may add more to this
    return {
        "statusCode": upstream_response.status_code,
        "headers": {k:v for k,v in upstream_response.headers.items() if k in header_whitelist},
      #  "body": upstream_response.text or "",
    }
