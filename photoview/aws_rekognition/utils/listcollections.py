import json
import dateutil

import boto3

from aws_rekognition.models import AWSRekognitionRequestResponse

def list_collections(rek_conn=boto3.client('rekognition')):
    
    res = rek_conn.list_collections()
    
    meta = res['ResponseMetadata']
    headers = meta['HTTPHeaders']
    AWSRekognitionRequestResponse.objects.create(requestId=meta['RequestId'], endpoint = 'list_collections', date = dateutil.parser.parse(headers['date']), statusCode = meta['HTTPStatusCode'], retryAttempts = meta['RetryAttempts'], responseLength = headers['content-length'], responseContentType = headers['content-type'], responseBody=json.dumps(res))
    
    return res