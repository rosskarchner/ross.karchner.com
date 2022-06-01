import json
import boto3
import mf2py

s3=boto3.client('s3')


def update_feeditems(bucket, key, table=None):
    pass


def process_events(events):
    for event in events:
        if event['eventName'].startswith('ObjectCreate'):
            bucket = event['s3']['bucket']['name']
            key = event['s3']['object']['key']
            html = s3.get_object(Bucket=bucket, Key=key)['Body'].read()
            parsed = mf2py.parse(doc=html)
            print(parsed)
        else:
            print("can't handle %s yet" % event['eventName'])

def lambda_handler(sqs_event,context):
    for record in sqs_event['Records']:
       contents = json.loads(record['body'])
       process_events(contents['Records'])
