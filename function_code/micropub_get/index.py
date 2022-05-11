import json
import os

def lambda_handler(event, context):
    print(event)
    return {
        'statusCode': 200,
        'body': json.dumps({'media-endpoint': os.environ['MEDIA_ENDPOINT']})
    }
