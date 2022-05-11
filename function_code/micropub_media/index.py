import json
import email
import base64
import boto3
from urllib.parse import urljoin
import os

s3 = boto3.client("s3")
bucket_name = os.environ['BUCKET']

def lambda_handler(event, context):
    request_id = event["requestContext"]["requestId"]
    # headers = multidict.CIMultiDict(event["headers"])
    if event.get("isBase64Encoded"):
        body = base64.b64decode(event["body"])
    else:
        body = event["body"]
    body_with_content_type = (
        b"Content-Type: "
        + bytes(event["headers"]["content-type"], encoding="utf-8")
        + b"\r\n"
        + body
    )
    msg = email.parser.BytesParser().parsebytes(body_with_content_type)


    for part in msg.get_payload():
        if part.get_param("name", header="content-disposition") == "file":
            filename = part.get_param("filename", header="content-disposition")
            file_data = part.get_payload(
                decode=True
            )
            content_type = part['Content-Type']

    key=f"media/{request_id}/{filename}"
    s3.put_object(Bucket=bucket_name, Key=key, Body=file_data, ContentType=content_type)

    url = urljoin(os.environ['ME_URL'],key)

    return {"statusCode": 201, "headers": {'Location':url }}
