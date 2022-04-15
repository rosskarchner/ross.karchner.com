import datetime
import os
import random
from urllib.parse import urljoin

import boto3
import multidict
import pytz
import slugify
from botocore.errorfactory import ClientError

from .auth import validate_token
from .normalize import normalize_micropub_post
from .render import document_to_html


def s3_object_exists(path):
    """
    check if an object exists in the destination S3 bucket
    """
    s3 = boto3.client("s3")
    try:
        return s3.head_object(Bucket=os.environ["BUCKET"], Key=path)
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

    slug_material = (
        document["properties"].get("mp-slug")
        or document["properties"].get("name")
        or [noise]
    )

    slug = slugify.slugify(slug_material)

    path = None

    while path is None:
        original_slug = slug
        speculative_path = "/%s/%s/%s.html" % (
            pubdate.year,
            pubdate.month,
            slug,
        )
        existing_item = s3_object_exists(speculative_path)
        if not existing_item:
            path = speculative_path
        else:
            slug = original_slug + "-" + random.randint(1, 1000)

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

    return document


def micropub_post(event, context):
    """
    interpret and act on incoming micropub post
    """
    headers = multidict.CIMultiDict(event["headers"])
    if headers.get("content-type") not in [
        "application/json",
        "application/x-www-form-urlencoded",
    ]:
        return {"statusCode": 415, "body": "unknown content-type"}

    if event["body"] == "":
        return {"statusCode": 400, "body": "missing body"}

    json_document, access_token = normalize_micropub_post(
        event, headers=headers)

    if access_token:
        valid, scopes = validate_token(access_token)
    else:
        return {"statusCode": 403, "body": "no access token found"}

    if not valid:
        return {"statusCode": 403, "body": "access token invalid or expired"}

    if "action" not in json_document:
        complete_document = annotate_new_post(json_document)
        # we're creating a new post

    elif json_document.get("action") == "update":
        pass
        # updating a post

    elif json_document.get("action") == "delete":
        pass
        # delete a post

    else:
        return {"statusCode": 400, "body": "not a supported action"}

    if valid and 'create' in scopes:
        print(scopes)
        # TODO: validate SCOPE!
        return {"statusCode": 202, "body": document_to_html(complete_document)}

    # document, access_token, files = normalize_micropub_post(event)
    # users = TokenUser(access_token)

    # required_scope = ScopeForOperation[operation]

    # if required_scope in users_scopes:
    #    url_path = create_document(operation, document)
    #    url = urljoin(os.environ["MeURL"], url_path)
    #    print(url)

    #   return {"statusCode": 200, "headers": {"Location": url}}
