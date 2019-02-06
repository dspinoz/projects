import sys
import os
import dateutil
from datetime import datetime
import json
import base64

import boto3

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from aws_rekognition.models import AWSRekognitionRequestResponse

class Command(BaseCommand):
  help = "Download archive"
  
  def add_arguments(self, parser):
    parser.add_argument('--detect', nargs='+', action='append', default=[], help="Objects to detect. Eg. 'faces', 'labels', 'text'")
    parser.add_argument('--image', nargs='?', type=str)
    parser.add_argument('--attributes', nargs='?', type=str, default="DEFAULT")
  
  def handle(self, *args, **options):
    if options['image'] is None:
      print("NO IMAGE PROVIDED, use --image")
      sys.exit(1)
    if not os.path.isfile(options['image']):
      print("THIS IS NOT A FILE!")
      sys.exit(1)
    if len(options['detect']) == 0:
      print("NO DETECTIONS PROVIDED")
      sys.exit(1)

    fd = open(options['image'], 'r+b')
    if fd is None:
      print("COULD NOT OPEN IMAGE FILE")
      sys.exit(1)
    
    for detect in options['detect']:
      detect = detect[0]
      print("Detecting {} from image".format(detect))
      
      fd.seek(0)
      
      rek_conn = boto3.client('rekognition')
    
      if detect == 'faces':
        res = rek_conn.detect_faces(Image={'Bytes': fd.read()})
      elif detect == 'labels':
        res = rek_conn.detect_labels(Image={'Bytes': fd.read()})
      elif detect == 'text':
        res = rek_conn.detect_text(Image={'Bytes': fd.read()})
    
      meta = res['ResponseMetadata']
      headers = meta['HTTPHeaders']
      AWSRekognitionRequestResponse.objects.create(requestId=meta['RequestId'], endpoint = 'detect_{}'.format(detect), date = dateutil.parser.parse(headers['date']), statusCode = meta['HTTPStatusCode'], retryAttempts = meta['RetryAttempts'], responseLength = headers['content-length'], responseContentType = headers['content-type'], responseBody=json.dumps(res))
    
      print(json.dumps(res))