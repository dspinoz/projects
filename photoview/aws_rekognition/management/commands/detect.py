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

import aws_rekognition.utils as u

class Command(BaseCommand):
  help = "Image detection"
  
  def add_arguments(self, parser):
    parser.add_argument('--detect', nargs='+', action='append', default=[], help="Objects to detect. Eg. 'faces', 'labels', 'text', 'celebrities'")
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
      
      u.detect(options['image'], fd)
