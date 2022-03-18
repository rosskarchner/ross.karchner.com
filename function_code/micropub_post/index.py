import base64
import json
import random
import datetime
import os
from xml.dom.expatbuilder import parseString
from urllib.parse import urljoin

from normalize import normalize_micropub_post
from auth import scopes_for_token

import multidict
import pytz
import slugify
import dateutil.parser

from granary.microformats2 import json_to_html

import boto3
from botocore.errorfactory import ClientError

""" 
import os
import random
import xml.etree.ElementTree
from datetime import datetime
from enum import Enum
from urllib.parse import parse_qsl, urljoin

import boto3

import pytz
import requests
from boto3.dynamodb.conditions import Key

import multidict
import slugify
#from auth import TokenUser



class MicropubOperationType(Enum):
    CREATE = 1
    UPDATE = 2
    DELETE = 3
    UNDELETE = 4
    MEDIA = 5


dynamodb = boto3.resource("dynamodb")
EntriesTable = dynamodb.Table(os.environ["TABLE"])


def remove_tags(text):
    return "".join(xml.etree.ElementTree.fromstring(text).itertext())


def micropub_get(event, context):
    print(json.dumps(event))
    return {
        "statusCode": 202,
        "body": "This site doesn't seem to belong to this subscriber",
        "headers": {"Location": "https://ross.karchner.com/fake"},
    }


def create_document(operation, document):
    timezone = pytz.timezone(os.environ["TIMEZONE"])
    now_local = timezone.fromutc(datetime.utcnow())
    now_iso = now_local.isoformat()

    noise = str(random.randint(1, 1000))

    # don't mess with publication date if it's already set
    if (
        "published" not in document["properties"]
        and "dt-published" not in document["properties"]
    ):
        document["properties"]["dt-published"] = [now_iso]
        pubdate = now_local

    else:
        pubdate_iso_list = document["properties"].get("dt-published") or document[
            "properties"
        ].get("published")

        pubdate_iso = pubdate_iso_list[0]
        pubdate = dateutil.parser.parse(pubdate_iso)

    # DO set the updated date
    if "updated" in document["properties"]:
        del document["properties"]["updated"]

    document["properties"]["dt-updated"] = [now_iso]

    # figure out the URL
    slug_material_list = (
        document["properties"].get("mp-slug")
        or document["properties"].get("name")
        or [noise]
    )

    slug = slugify.slugify(slug_material_list)

    url = None

    while url == None:
        extra_slug = random.randint(1, 1000)
        speculative_url = "/%s/%s/%s-%s.html" % (
            pubdate.year,
            pubdate.month,
            extra_slug,
            slug,
        )
        existing_item = EntriesTable.get_item(Key={"url": speculative_url}).get("Item")
        if not existing_item:
            url = speculative_url

    year_month = "%s%s" % (pubdate.year, str(pubdate.month).zfill(2))
    sortdate = now_iso + "&&" + noise


    return url


def scope_required_for_document(document):
    if "action" in document and document["action"] in ["update", "delete", "undelete"]:
        operation = getattr(MicropubOperationType, document["action"].uppercase())
    elif "type" in document and "properties" and document["properties"]:
        operation = MicropubOperationType.CREATE
 """

def s3_object_exists(path):
    s3 = boto3.client('s3')
    try:
        return s3.head_object(Bucket=os.environ['BUCKET'], Key=path)
    except ClientError:
        # Not found
        return False


def annotate_new_post(document, update = False):
    timezone = pytz.timezone(os.environ["TZ"])
    now_local = timezone.fromutc(datetime.datetime.utcnow())
    now_iso = now_local.isoformat()

    noise = str(random.randint(1, 1000))

    # don't mess with publication date if it's already set
    if 'properties' not in document:
        document['properties'] = {}
        
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

    while path == None:
        extra_slug = random.randint(1, 1000)
        speculative_path = "/%s/%s/%s-%s.html" % (
            pubdate.year,
            pubdate.month,
            extra_slug,
            slug,
        )
        existing_item = s3_object_exists(speculative_path)
        if not existing_item:
            path = speculative_path

    document['properties']['url']= [urljoin(os.environ['ME_URL'], path)]
    return document


def micropub_post(event, context):
    print(event)
    headers = multidict.CIMultiDict(event["headers"])
    if headers.get("content-type") not in [
        "application/json",
        "application/x-www-form-urlencoded"
    ]:
        return {"statusCode": 415, "body": "unknown content-type"}

    if event['body'] == '':
        return {"statusCode": 400, "body": "missing body"}

    json_document, access_token = normalize_micropub_post(event, headers=headers)

    if access_token:
        scopes = scopes_for_token(access_token)
        print(scopes)
    else:
        return {"statusCode": 403, "body": "no access token found"}

    if 'action' not in json_document:
        complete_document = annotate_new_post(json_document)
        # we're creating a new post

    elif json_document.get('action') == 'update':
        pass
        # updating a post


    elif json_document.get('action') == 'delete':
        pass
        # delete a post

    else:
        return {"statusCode": 400, "body": "not a supported action"}

    if access_token:
        scopes = scopes_for_token(access_token)
        # TODO: validate SCOPE!
        return {"statusCode": 202, "body": json_to_html(complete_document)}
    # document, access_token, files = normalize_micropub_post(event)
    # users = TokenUser(access_token)

    # required_scope = ScopeForOperation[operation]

    # if required_scope in users_scopes:
    #    url_path = create_document(operation, document)
    #    url = urljoin(os.environ["MeURL"], url_path)
    #    print(url)

    #   return {"statusCode": 200, "headers": {"Location": url}}
