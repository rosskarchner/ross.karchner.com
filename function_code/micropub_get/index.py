import json
import os


def lambda_handler(event, context):
    q_param = event["queryStringParameters"].get("q")

    if q_param == "config":
        return {
            "statusCode": 200,
            "body": json.dumps({"media-endpoint": os.environ["MEDIA_ENDPOINT"]}),
        }
