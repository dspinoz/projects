import boto3

from log_response import log_response



import sys
import os
import dateutil
from datetime import datetime
import json
import base64
import hashlib
import mimetypes
import tempfile

import boto3
from PIL import Image

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File

from aws_rekognition.models import AWSRekognitionRequestResponse
from aws_rekognition.models import IndexedImage, ConvertedImage
from aws_rekognition.models import DetectionType, Detection, ImageDetection




def request_detection(fd, detect='faces', rek_conn=boto3.client('rekognition')):
  
  endpoint = 'detect_{}'.format(detect)
  
  if detect == 'faces':
    res = rek_conn.detect_faces(Image={'Bytes': fd.read()})
  elif detect == 'labels':
    res = rek_conn.detect_labels(Image={'Bytes': fd.read()})
  elif detect == 'text':
    res = rek_conn.detect_text(Image={'Bytes': fd.read()})
  elif detect == 'celebrities':
    res = rek_conn.recognize_celebrities(Image={'Bytes': fd.read()})
    endpoint = 'recognize_celebrities'

  log_response(endpoint, res)
  
  #TODO debug(json.dumps(res))
  
def determineThumbsSize(width):
  sizes = []
  sz = width
  while sz > 32: #dont go smaller than 16 pixels, too small to see anything useful!
    sz = sz/2
    sizes.append(sz)
  # convert to nearest base 2 sizes
  sizes2 = []
  for i in sizes:
    exp = 1
    base = 2
    while i > base:
      i = i / base
      exp = exp + 1
    sizes2.append(2**exp)
  return sizes2
  
def detect(path, fd=None, detections=['faces'], hasher=hashlib.sha256(), generateThumbs=True, rek_conn=boto3.client('rekognition')):
  
  if not fd:
    fd = open(path, 'r+b')
  
  img = Image.open(fd)
  
  imgBB = img.getbbox()
  imgPixels = img.load()
  
  imgWidth = imgBB[2] - imgBB[0]
  imgHeight = imgBB[3] - imgBB[1]
  
  hexdigest = None
  if hasher:
    fd.seek(0)
    while True:
      b = fd.read()
      if not b:
        break
      hasher.update(b"".join(b))
    hexdigest = hasher.hexdigest()
    
  indexedImage = IndexedImage.objects.create(filePath=os.path.realpath(path), sha256=hexdigest, width=imgWidth, height=imgHeight, contentType=mimetypes.guess_type(path)[0])
  
  if generateThumbs:
    for tsize in determineThumbsSize(imgWidth):
      thumb = ConvertedImage.objects.create(orig=indexedImage)
      with tempfile.SpooledTemporaryFile(max_size=10000000, mode='w+b') as t:
        cpy = img.copy()
        cpy.thumbnail((tsize, tsize))
        cpy.save(t, 'png')
        t.flush()
        t.seek(0)
        thumb.file.save('thumb{}'.format(tsize), File(t))
  
  return indexedImage


