import sys
import os
import dateutil
from datetime import datetime
import json
import base64
import tempfile
import subprocess

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
    parser.add_argument('--force', action='store_true', default=False)
  
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
    
    detections = []
    
    if len(options['detect']) == 1 and options['detect'][0][0] == 'none':
      # leave detections empty
      pass
    else:
      for detect in options['detect']:
        detections.append(detect[0])
    
    
    image = options['image']
    attemptedConversion = False
          
    while True:
      with tempfile.NamedTemporaryFile(mode='w+b', suffix=".jpg") as t:
      
        try:
          if attemptedConversion:
            print("Retrying image detection")
          else:
            print("Detecting {} from image".format(detections))
            
          u.detect(image, fd, detections, rerun=options['force'])
          
          break
        except IOError as e:
          if attemptedConversion:
            raise e
          if not e.message.startswith("cannot identify image file"):
            raise e
          
          print("Generating image preview...")
          previewImageBytes = subprocess.Popen("exiftool -Composite:PreviewImage -b '{}'".format(os.path.realpath(image)), shell=True, stdout=subprocess.PIPE).stdout.read()
        
          t.write(previewImageBytes)
          t.flush()
          
          attemptedConversion = True
          image = t.name
          fd = open(t.name, 'r+b')
