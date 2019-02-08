import hashlib
import json
import os
import mimetypes
import tempfile

import boto3
from PIL import Image

from django.core.files import File

from aws_rekognition.models import AWSRekognitionRequestResponse
from aws_rekognition.models import IndexedImage, ConvertedImage
from aws_rekognition.models import DetectionType, Detection, ImageDetection

from log_response import log_response

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
  return res
  
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
  
def detect(path, fd=None, detections=['faces'], hasher=hashlib.sha256(), generateThumbs=True, captureDetections=True, rek_conn=boto3.client('rekognition')):
  
  if not fd:
    fd = open(path, 'r+b')
  
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
  
  for detect in detections:
    
    fd.seek(0)
    res = request_detection(fd, detect, rek_conn)
    
    print(json.dumps(res))
    
    if 'FaceDetails' in res and res['FaceDetails'] is not None:
      for face in res['FaceDetails']:
        detectedFace((img, imgWidth, imgHeight), indexedImage, face, DetectionType.FACE)
        
        if capturePixels:
          bb = calcBB((imgWidth, imgHeight), face['BoundingBox'])
          drawBB(capturePixels, (0,0,255), bb) #BLUE
    
    
    if 'CelebrityFaces' in res:
      for face in res['CelebrityFaces']:
        # face but probably has an identifier of some sort?
        detectedFace((img, imgWidth, imgHeight), indexedImage, face, DetectionType.CELEBRITY)
          
        if capturePixels:
          bb = calcBB((imgWidth, imgHeight), face['BoundingBox'])
          drawBB(capturePixels, (135,206,250), bb) #LIGHTSKYBLUE
    
    
    if 'UnrecognizedFaces' in res:
      for face in res['UnrecognizedFaces']:
        detectedFace((img, imgWidth, imgHeight), indexedImage, face, DetectionType.FACE_UNKNOWN)
          
      if capturePixels:
        bb = calcBB((imgWidth, imgHeight), face['BoundingBox'])
        drawBB(capturePixels, (70,130,180), bb) #STEELEBLUE
    
    
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
        
        if capturePixels:
          drawBB(capturePixels, color, bb)
    
    
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
          
          if capturePixels:
            drawBB(capturePixels, (255,0,0), bb) #RED
  
  
  if imgDetections:
    with tempfile.SpooledTemporaryFile(max_size=10000000, mode='w+b') as t:
      size = determineThumbsSize(imgWidth)[0]
      imgDetections.resize((size, size))
      imgDetections.save(t, 'png')
      t.flush()
      t.seek(0)
      detectionsThumb = ConvertedImage.objects.create(orig=indexedImage,metadata=json.dumps({"Type":"detections", "DetectionsInfo":detections}))
      detectionsThumb.file.save('dthumb{}'.format(256), File(t))
  
  
  return indexedImage


