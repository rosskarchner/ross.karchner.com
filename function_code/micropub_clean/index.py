import datetime
import os
import random
from urllib.parse import urljoin, urlparse
import json
import boto3
import multidict
import pytz
import slugify
import mf2util
from botocore.errorfactory import ClientError

from render import document_to_html

from htmllaundry import strip_markup

s3 = boto3.client("s3")
bucket_name = os.environ["BUCKET"]


def s3_object_exists(path):
    """
    check if an object exists in the destination S3 bucket
    """
    try:
        return s3.head_object(Bucket=bucket_name, Key=path)
    except ClientError:
        # Not found
        return False


def annotate_new_post(document, update=False):
    """
    Take an incoming post, and add publication date, set path
    and other useful things
    """
    timezone = pytz.timezone(os.environ["TZ"])
    now_local = timezone.fromutc(datetime.datetime.utcnow())
    now_iso = now_local.isoformat()

    noise = str(random.randint(1, 1000))

    # don't mess with publication date if it's already set
    if "properties" not in document:
        document["properties"] = {}

    if (
        "published" not in document["properties"]
        and "dt-published" not in document["properties"]
    ):
        document["properties"]["published"] = [now_iso]
        pubdate = now_local
    else:
    
        pubdate_raw = (
            document["properties"].get("published")
            or document["properties"].get("dt-published")
        )[0]
        pubdate = mf2util.parse_datetime(pubdate_raw)

    slug_material = (
        document["properties"].get("mp-slug")
        or document["properties"].get("name")
        or [noise]
    )

    slug = slugify.slugify(slug_material)

    path = None

    while path is None:
        original_slug = slug
        speculative_path = "%s/%s/%s.html" % (
            pubdate.year,
            pubdate.month,
            slug,
        )
        existing_item = s3_object_exists(speculative_path)
        if not existing_item:
            path = speculative_path
        else:
            slug = original_slug + "-" + str(random.randint(1, 1000))

    post_url = urljoin(os.environ["ME_URL"], path)
    document["properties"]["url"] = [post_url]
    document["properties"]["author"] = [
        {
            "type": ["h-card"],
            "properties": {
                "name": [os.environ["AUTHOR_NAME"]],
                "url": [os.environ["ME_URL"]],
            },
        }
    ]

    content_list = document["properties"].get("content", [])
    for content_item in content_list:
        if isinstance(content_item, dict) and "html" in content_item:
            content_item["value"] = strip_markup(content_item["html"])

    return document


def lambda_handler(event, context):
    """
    interpret and act on incoming micropub post
    """
    headers = multidict.CIMultiDict(event["headers"])
    scopes = event['requestContext']['authorizer']['lambda']['scopes']

    if event["body"] == "":
        return {"statusCode": 400, "body": "missing body"}

    if headers["content-type"] == "application/json":
        json_document = json.loads(event["body"])

    action = json_document.get("action", "create")

    if action not in scopes:
        return {
            "statusCode": 403,
            "body": json.dumps({"error": "insufficient_scope", "scope": action}),
        }
    
    if action == "create":
        complete_document = annotate_new_post(json_document)
        url = complete_document["properties"]["url"][0]
        print(complete_document)
        key = urlparse(url).path[1:]  #
        html = document_to_html(complete_document)
        s3.put_object(Bucket=bucket_name, Key=key, Body=html, ContentType="text/html")

        return {"statusCode": 201, "headers": {"Location": url}}