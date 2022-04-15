import json
import os
import string
from granary import microformats2

microformats2.HENTRY = string.template(open('HENTRY.template', encoding=='utf-8').read())

def lambda_handler(event, context):
    # TODO implement



    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
