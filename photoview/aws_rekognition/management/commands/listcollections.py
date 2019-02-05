import json
import dateutil

import boto3

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from aws_rekognition.models import AWSRekognitionRequestResponse

class Command(BaseCommand):
  help = "List Collections"
  
  def handle(self, *args, **options):
    rek_conn = boto3.client('rekognition')
    
    res = rek_conn.list_collections()
    
    meta = res['ResponseMetadata']
    headers = meta['HTTPHeaders']
    AWSRekognitionRequestResponse.objects.create(requestId=meta['RequestId'], endpoint = 'list_collections', date = dateutil.parser.parse(headers['date']), statusCode = meta['HTTPStatusCode'], retryAttempts = meta['RetryAttempts'], responseLength = headers['content-length'], responseContentType = headers['content-type'], responseBody=json.dumps(res))
    
    print(json.dumps(res))