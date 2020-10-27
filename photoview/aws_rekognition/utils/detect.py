from datetime import datetime
import dateutil
import hashlib
import json
import os
import mimetypes
import tempfile
import sys
import subprocess

import boto3
from PIL import Image

from django.core.files import File
from django.conf import settings

from photoview.models import IndexedImage, ConvertedImage
import photoview.utils

from aws_rekognition.models import AWSRekognitionRequestResponse
from aws_rekognition.models import DetectionType, Detection, ImageDetection, DetectionRun

from log_response import log_response

def calcBB((width, height), featureBB):
  bb = (featureBB['Left'], featureBB['Top'], featureBB['Left']+featureBB['Width'], featureBB['Top'] + featureBB['Height'])
  
  left = int(bb[0]*width)
  upper = int(bb[1]*height)
  right = int(bb[2]*width)
  lower = int(bb[3]*height)
  
  return (left, upper, right, lower)
  
def drawBB(img, color, bb, calc=False, width=None, height=None, imageBB=None):
  if calc:
    bb = calcBB((width, height), bb)
  
  left = bb[0]
  upper = bb[1]
  right = bb[2]
  lower = bb[3]
  
  if left < imageBB[0]:
    left = imageBB[0]
  if upper < imageBB[1]:
    upper = imageBB[1]
  if right > imageBB[2]:
    right = imageBB[2] - 1
  if lower > imageBB[3]:
    lower = imageBB[3] - 1
  
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
    print("Saved {} '{}' as detection image".format(type, fname))

def fake_request_detection(detect, responseId):
  res = AWSRekognitionRequestResponse.objects.get(id=responseId)
  return json.loads(res.responseBody)


def request_detection(fd, detect='faces', rek_conn=boto3.client('rekognition')):
  
  res = None
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
  return res

def get_detection_object(type):
  if type == 'faces':
    return Detection.objects.get_or_create(type=DetectionType.FACE)[0]
  if type == 'labels':
    return Detection.objects.get_or_create(type=DetectionType.LABEL)[0]
  if type == 'text':
    return Detection.objects.get_or_create(type=DetectionType.TEXT_ANY)[0]
  if type == 'celebrities':
    return Detection.objects.get_or_create(type=DetectionType.CELEBRITY)[0]
  return None


def detect(path, detections=['faces'], hasher=hashlib.sha256(), generateThumbs=True, captureDetections=True, rerun=False, rek_conn=boto3.client('rekognition'), runExifTool=True, convertUnknownImages=True):
  
  (indexedImage, createdIndexedImage) = photoview.utils.getIndexedImage(path)
  
  if not indexedImage:
    return None
  
  detectionsToRun = []
  
  if not rerun:
    for detect in detections:
      runs = DetectionRun.objects.filter(image=indexedImage, detection=get_detection_object(detect))
      
      if runs.count() > 0:
        print("{} detection has already been run".format(detect))
      else:
        print("{} detection can run".format(detect))
        detectionsToRun.append(detect)
  
  if len(detectionsToRun) == 0:
    return indexedImage
  
  forDetect = ConvertedImage.objects.filter(orig=indexedImage).filter(metadata__iregex=r'"Type": "thumbnail"').filter(size__lte=50000).order_by("-size")
  forDetect = forDetect[0]
  print("Selected conversion (id={}) for detections: {}".format(forDetect.id, os.path.join(settings.MEDIA_ROOT,forDetect.file.name)))
  
  
  fd = open(os.path.join(settings.MEDIA_ROOT,forDetect.file.name), 'r+b')
  
  img = Image.open(fd)
  
  imgBB = img.getbbox()
  imgPixels = img.load()
  
  imgWidth = imgBB[2] - imgBB[0]
  imgHeight = imgBB[3] - imgBB[1]
  
  imgDetections = None
  capturePixels = None
  if captureDetections:
    imgDetections = img.copy()
    capturePixels = imgDetections.load()
  
  if len(detectionsToRun) == 0:
    print("WARNING: No detections to run")
  
  for detect in detectionsToRun:
    
    fd.seek(0)
    res = request_detection(fd, detect, rek_conn)
    # /media/daniel/EXPANSION02/EXPANSION/photos/15.01 liliana arrival/IMG_5202.JPG
    #res = fake_request_detection(detect, 10)
    
    DetectionRun.objects.create(detection=get_detection_object(detect), image=indexedImage)
    
    #print(json.dumps(res))
    
    if 'FaceDetails' in res and res['FaceDetails'] is not None:
      for face in res['FaceDetails']:
        detectedFace((img, imgWidth, imgHeight), indexedImage, face, DetectionType.FACE)
        
        if capturePixels:
          bb = calcBB((imgWidth, imgHeight), face['BoundingBox'])
          try:
            drawBB(capturePixels, (0,0,255), bb, imageBB=imgBB) #BLUE
          except:
            print("GOT EXCEPTION")
            pass
    
    
    if 'CelebrityFaces' in res:
      for celeb in res['CelebrityFaces']:
        
        (detection, createdDetection) = Detection.objects.get_or_create(type=DetectionType.CELEBRITY)
        
        idet = ImageDetection.objects.create(image=indexedImage, detection=detection, confidence=celeb['MatchConfidence'], identifier=celeb['Name'], metadata=json.dumps(celeb))
        
        face = celeb['Face']
        detectedFace((img, imgWidth, imgHeight), indexedImage, face, DetectionType.CELEBRITY_FACE)
          
        if capturePixels:
          bb = calcBB((imgWidth, imgHeight), face['BoundingBox'])
          drawBB(capturePixels, (135,206,250), bb, imageBB=imgBB) #LIGHTSKYBLUE
    
    
    if 'UnrecognizedFaces' in res:
      for face in res['UnrecognizedFaces']:
        detectedFace((img, imgWidth, imgHeight), indexedImage, face, DetectionType.FACE_UNKNOWN)
          
      if capturePixels:
        bb = calcBB((imgWidth, imgHeight), face['BoundingBox'])
        drawBB(capturePixels, (70,130,180), bb, imageBB=imgBB) #STEELEBLUE
    
    
    if 'TextDetections' in res:
    
      for text in res['TextDetections']:
        
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
          print("Saved {} '{}' as detection image".format(text['Type'], text['DetectedText']))
        
        if capturePixels:
          drawBB(capturePixels, color, bb, imageBB=imgBB)
    
    
    if 'Labels' in res:
      for label in res['Labels']:
        
        (detection, createdDetection) = Detection.objects.get_or_create(type=DetectionType.LABEL)
        
        idet = ImageDetection.objects.create(image=indexedImage, detection=detection, confidence=label['Confidence'], identifier=label['Name'], metadata=json.dumps(label))
        
        for instance in label['Instances']:
          
          (detection, createdDetection) = Detection.objects.get_or_create(type=DetectionType.LABEL)
          
          bb = instance['BoundingBox']
          
          idet = ImageDetection.objects.create(image=indexedImage, detection=detection, confidence=instance['Confidence'], identifier=label['Name'], boundingBoxTop=bb['Top'], boundingBoxHeight=bb['Height'], boundingBoxWidth=bb['Width'], boundingBoxLeft=bb['Left'], metadata=json.dumps(instance))
          
          bb = calcBB((imgWidth, imgHeight), bb)
          
          with tempfile.SpooledTemporaryFile(max_size=10000000, mode='w+b') as t:
            img.crop(bb).save(t, 'png')
            t.flush()
            t.seek(0)
            idet.file.save('png', File(t))
            print("Saved {} '{}' as detection image".format(DetectionType.LABEL, label['Name']))
          
          if capturePixels:
            drawBB(capturePixels, (255,0,0), bb, imageBB=imgBB) #RED
  
  
  if len(detectionsToRun) and imgDetections:
    with tempfile.SpooledTemporaryFile(max_size=10000000, mode='w+b') as t:
      size = photoview.utils.determineThumbsSize(imgWidth)[0]
      imgDetections.thumbnail((size, size))
      imgDetections.save(t, 'png')
      t.flush()
      detectionsThumb = ConvertedImage.objects.create(orig=indexedImage,size=t.tell(),metadata=json.dumps({"Type":"detections", "DetectionsInfo":detectionsToRun, "Width": size}))
      t.seek(0)
      detectionsThumb.file.save('dthumb{}'.format(size), File(t))
      print("Saved {} '{}' as converted image".format('detections', detectionsToRun))
  
  
  return indexedImage
