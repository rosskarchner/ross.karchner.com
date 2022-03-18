
import json
import multidict
import email

def lambda_handler(event, context):
    # TODO implement
    headers = multidict.CIMultiDict(event["headers"])
    if headers["content-type"].startswith("multipart/form-data"):
        content_type = event["headers"]["content-type"]
        body_with_content_type = (
            b"Content-Type: " + content_type.encode() + b"\r\n" + body
        )
        msg = email.parser.BytesParser().parsebytes(body_with_content_type)

        files = {
            part.get_param("filename", header="content-disposition"): part.get_payload(
                decode=False
            )
            for part in msg.get_payload()
            if part.get_param("filename", header="content-disposition")
        }
        json_document, body_access_token = kvpairs_to_mfjson(kvpairs)

        return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
