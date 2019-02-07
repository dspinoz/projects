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

def detectedFace((img, width, height), index, face, type=DetectionType.FACE):

  (detection, createdDetection) = Detection.objects.get_or_create(type=type)
  
  bb = face['BoundingBox']
  
  idet = ImageDetection.objects.create(image=index, detection=detection, confidence=face['Confidence'], boundingBoxTop=bb['Top'], boundingBoxHeight=bb['Height'], boundingBoxWidth=bb['Width'], boundingBoxLeft=bb['Left'], metadata=json.dumps(face))
  
  bb = calcBB((width, height), bb)
  
  with tempfile.SpooledTemporaryFile(max_size=10000000, mode='w+b') as t:
    img.crop(bb).save(t, 'png')
    t.flush()
    t.seek(0)
    
    fname = 'uface'
    if type == DetectionType.FACE:
      fname = 'face'
    elif type == DetectionType.FACE_UNKNOWN:
      fname = 'uface'
    elif type == DetectionType.CELEBRITY:
      fname = 'celeb'
    
    idet.file.save(fname, File(t))

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
    indexedImage = None
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
      
      indexedImage = IndexedImage.objects.create(filePath=os.path.realpath(options['image']), sha256=hasher.hexdigest(), width=imgWidth, height=imgHeight, contentType=mimetypes.guess_type(options['image'])[0])
      
      for tsize in determineThumbsSize(imgWidth):
      
        thumb = ConvertedImage.objects.create(orig=indexedImage)
        with tempfile.SpooledTemporaryFile(max_size=10000000, mode='w+b') as t:
          cpy = img.copy()
          cpy.thumbnail((tsize, tsize))
          cpy.save(t, 'png')
          t.flush()
          t.seek(0)
          thumb.file.save('thumb{}'.format(tsize), File(t))
      
      
      
    detections = []
    
    for detect in options['detect']:
      detect = detect[0]
      detections.append(detect)
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
            detectedFace((img, imgWidth, imgHeight), indexedImage, face, DetectionType.FACE)
            
            bb = calcBB((imgWidth, imgHeight), face['BoundingBox'])
            drawBB(imgPixels, (0,0,255), bb) #BLUE
            
            #f = img.crop(bb)
            #f.show()
      if 'TextDetections' in res:
      
        for text in res['TextDetections']:
          print(text['DetectedText'], text['Confidence'], text['Type'], text['Id'])
          if img:
            (detection, createdDetection) = Detection.objects.get_or_create(type=DetectionType.TEXT_LINE)
            color = (0,100,0) #LINE DARKGREEN
            if text['Type'] == "WORD":
              (detection, createdDetection) = Detection.objects.get_or_create(type=DetectionType.TEXT_WORD)
              color = (50,205,50) #LIMEGREEN
            
            bb = text["Geometry"]["BoundingBox"]
            
            idet = ImageDetection.objects.create(image=indexedImage, detection=detection, confidence=text['Confidence'], identifier=text['Id'], boundingBoxTop=bb['Top'], boundingBoxHeight=bb['Height'], boundingBoxWidth=bb['Width'], boundingBoxLeft=bb['Left'], metadata=json.dumps(text))
            
            bb = calcBB((imgWidth, imgHeight), bb)
            
            with tempfile.SpooledTemporaryFile(max_size=10000000, mode='w+b') as t:
              img.crop(bb).save(t, 'png')
              t.flush()
              t.seek(0)
              idet.file.save('png', File(t))
            
            drawBB(imgPixels, color, text["Geometry"]["BoundingBox"], True, imgWidth, imgHeight)
      if 'Labels' in res:
        for label in res['Labels']:
          parentsList = []
          for parent in label['Parents']:
            parentsList.append(parent['Name'])
          parentsList.append(label['Name'])
          
          (detection, createdDetection) = Detection.objects.get_or_create(type=DetectionType.LABEL)
          idet = ImageDetection.objects.create(image=indexedImage, detection=detection, confidence=label['Confidence'], identifier=label['Name'], metadata=json.dumps(label))
          
          
          print("->".join(parentsList), label['Confidence'], len(label['Instances']))
          for instance in label['Instances']:
            if img:
              print("  ", instance['Confidence'])
              
              (detection, createdDetection) = Detection.objects.get_or_create(type=DetectionType.LABEL)
              
              bb = instance['BoundingBox']
              
              idet = ImageDetection.objects.create(image=indexedImage, detection=detection, confidence=instance['Confidence'], identifier=label['Name'], boundingBoxTop=bb['Top'], boundingBoxHeight=bb['Height'], boundingBoxWidth=bb['Width'], boundingBoxLeft=bb['Left'], metadata=json.dumps(instance))
              
              bb = calcBB((imgWidth, imgHeight), bb)
              
              with tempfile.SpooledTemporaryFile(max_size=10000000, mode='w+b') as t:
                img.crop(bb).save(t, 'png')
                t.flush()
                t.seek(0)
                idet.file.save('png', File(t))
              
              drawBB(imgPixels, (255,0,0), instance["BoundingBox"], True, imgWidth, imgHeight) #RED
            else:
              print("  ",instance['Confidence'])
      if 'CelebrityFaces' in res:
        for face in res['CelebrityFaces']:
          print("CELEBRITY",face)
          if img:
            # face but probably has an identifier of some sort?
            detectedFace((img, imgWidth, imgHeight), indexedImage, face, DetectionType.CELEBRITY)
            
            bb = calcBB((imgWidth, imgHeight), face['BoundingBox'])
            drawBB(imgPixels, (135,206,250), bb) #LIGHTSKYBLUE
      if 'UnrecognizedFaces' in res:
        for face in res['UnrecognizedFaces']:
          print("UNRECOGNISED",face)
          if img:
          
            detectedFace((img, imgWidth, imgHeight), indexedImage, face, DetectionType.FACE_UNKNOWN)
            
            bb = calcBB((imgWidth, imgHeight), face['BoundingBox'])
            drawBB(imgPixels, (70,130,180), bb) #STEELEBLUE
        
    
    with tempfile.SpooledTemporaryFile(max_size=10000000, mode='w+b') as t:
      cpy = img.copy()
      cpy.thumbnail((256, 256))
      cpy.save(t, 'png')
      t.flush()
      t.seek(0)
      detectionsThumb = ConvertedImage.objects.create(orig=indexedImage,metadata=json.dumps({"Type":"detections", "Detections":detections}))
      detectionsThumb.file.save('dthumb{}'.format(256), File(t))
  
    if img:
      img.show()