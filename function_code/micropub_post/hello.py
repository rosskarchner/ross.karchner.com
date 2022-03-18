import json


def hello(event, context):
    print(json.dumps(event))
    return {"statusCode": 202, "body": json.dumps("Hello from Lambda!")}
