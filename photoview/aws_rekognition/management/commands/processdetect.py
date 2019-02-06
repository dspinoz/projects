import sys
import os
import dateutil
from datetime import datetime
import json
import base64
import hashlib

import boto3
from PIL import Image

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from aws_rekognition.models import AWSRekognitionRequestResponse

def calcBB((width, height), featureBB):
  bb = (featureBB['Left'], featureBB['Top'], featureBB['Left']+featureBB['Width'], featureBB['Top'] + featureBB['Height'])
  
  left = int(bb[0]*width)
  upper = int(bb[1]*height)
  right = int(bb[2]*width)
  lower = int(bb[3]*height)
  
  return (left, upper, right, lower)
  
def drawBB(img, color, bb, calc=False, width=None, height=None):
  if calc:
    bb = calcBB((width, height), bb)
  
  left = bb[0]
  upper = bb[1]
  right = bb[2]
  lower = bb[3]
  
  for x in range(left, right):
    img[x,upper] = color
  for y in range(upper, lower):
    img[right,y] = color
  for x in range(left, right):
    img[x,lower] = color
  for y in range(upper, lower):
    img[left, y] = color

class Command(BaseCommand):
  help = "Download archive"
  
  def add_arguments(self, parser):
    parser.add_argument('--detect', nargs='+', action='append', default=[], help="Objects to detect. Eg. 'faces', 'labels', 'text', 'celebrities'")
    parser.add_argument('--image', nargs='?', type=str)
  
  def handle(self, *args, **options):
    if len(options['detect']) == 0:
      print("NO DETECTIONS PROVIDED")
      sys.exit(1)
    if options['image'] and not os.path.isfile(options['image']):
      print("THIS IS NOT A FILE!")
      sys.exit(1)
    
    if len(options['detect']) == 1 and options['detect'][0][0] == "*":
      print("DETECT ALL")
      options['detect'] = [['faces'], ['text'], ['labels'], ['celebrities']]
    
    img = None
    imgBB = None
    imgPixels = None
    imgWidth = None
    imgHeight = None
    if options['image']:
      img = Image.open(options['image'])
      imgBB = img.getbbox()
      imgPixels = img.load()
      
      imgWidth = imgBB[2] - imgBB[0]
      imgHeight = imgBB[3] - imgBB[1]
      
      fd = open(options['image'], 'r+b')
      hasher = hashlib.sha256()
      while True:
        b = fd.read()
        if not b:
          break
        hasher.update(b"".join(b))
      print("IMAGE HASH", hasher.hexdigest())
      fd.close()
      fd = None
    
    for detect in options['detect']:
      detect = detect[0]
      print("Detecting {} from image".format(detect))
    
      res = None
      if detect == 'faces':
        res = json.loads("""
...
        """)
      elif detect == 'labels':
        res = json.loads("""
...
        """)
      elif detect == 'text':
        res = json.loads("""
...
        """)
      elif detect == 'celebrities':
        res = json.loads("""
...
        """)
      if res is None:
        print("UNKNOWN DETECTION MODE", detect)
        sys.exit(1)
      #print(json.dumps(res))
      
      if 'FaceDetails' in res:
        for face in res['FaceDetails']:
          print(face)
          if img:
            bb = calcBB((imgWidth, imgHeight), face['BoundingBox'])
            #f = img.crop(bb)
            #f.show()
            drawBB(imgPixels, (0,0,255), bb) #BLUE
      if 'TextDetections' in res:
        for text in res['TextDetections']:
          print(text['DetectedText'], text['Confidence'], text['Type'], text['Id'])
          if img:
            color = (0,100,0) #LINE DARKGREEN
            if text['Type'] == "WORD":
              color = (50,205,50) #LIMEGREEN
            drawBB(imgPixels, color, text["Geometry"]["BoundingBox"], True, imgWidth, imgHeight)
      if 'Labels' in res:
        for label in res['Labels']:
          parentsList = []
          for parent in label['Parents']:
            parentsList.append(parent['Name'])
          parentsList.append(label['Name'])
          print("->".join(parentsList), label['Confidence'], len(label['Instances']))
          for instance in label['Instances']:
            if img:
              print("  ", instance['Confidence'])
              drawBB(imgPixels, (255,0,0), instance["BoundingBox"], True, imgWidth, imgHeight) #RED
            else:
              print("  ",instance['Confidence'])
      if 'CelebrityFaces' in res:
        for face in res['CelebrityFaces']:
          print("CELEBRITY",face)
          if img:
            bb = calcBB((imgWidth, imgHeight), face['BoundingBox'])
            drawBB(imgPixels, (135,206,250), bb) #LIGHTSKYBLUE
      if 'UnrecognizedFaces' in res:
        for face in res['UnrecognizedFaces']:
          print("UNRECOGNISED",face)
          if img:
            bb = calcBB((imgWidth, imgHeight), face['BoundingBox'])
            drawBB(imgPixels, (70,130,180), bb) #STEELEBLUE
        
    
    if img:
      img.show()