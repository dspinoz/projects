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

from aws_rekognition.models import AWSRekognitionRequestResponse
from aws_rekognition.models import IndexedImage, ConvertedImage
from aws_rekognition.models import DetectionType, Detection, ImageDetection, DetectionRun

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
    print("Saved {} '{}' as detection image".format(type, fname))


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

def detect(path, fd=None, detections=['faces'], hasher=hashlib.sha256(), generateThumbs=True, captureDetections=True, rerun=False, rek_conn=boto3.client('rekognition'), runExifTool=True, convertUnknownImages=True):
  
  createdIndexedImage = False
  indexedImage = None
  try:
    indexedImage = IndexedImage.objects.get(filePath=os.path.realpath(path))
    print("Image already indexed")
  except IndexedImage.DoesNotExist:
    
    if fd is None:
      fd = open(os.path.realpath(path), 'r+b')
    
    hexdigest = None
    if hasher:
      fd.seek(0)
      while True:
        b = fd.read()
        if not b:
          break
        hasher.update(b"".join(b))
      hexdigest = hasher.hexdigest()
    
    
    exifinfo = None
    if runExifTool:
      exifinfostr = subprocess.Popen("exiftool -j '{}'".format(os.path.realpath(path)), shell=True, stdout=subprocess.PIPE).stdout.read()
      if len(exifinfostr) == 0:
        print("WARNING: Could not generate exif metadata from {}".format(path))
      else:
        exifinfo = json.loads(exifinfostr)[0]
    
    
    indexedImage = IndexedImage.objects.create(filePath=os.path.realpath(path), sha256=hexdigest, width=exifinfo['ImageWidth'], height=exifinfo['ImageHeight'], contentType=mimetypes.guess_type(path)[0], size=fd.tell())
    createdIndexedImage = True
    
  
    previewImageBytes = subprocess.Popen("exiftool -Composite:PreviewImage -b '{}'".format(os.path.realpath(path)), shell=True, stdout=subprocess.PIPE).stdout.read()
    if len(previewImageBytes) > 0:
      with tempfile.NamedTemporaryFile(mode='w+b', suffix=".jpg") as t:
        t.write(previewImageBytes)
        t.flush()
        
        prev = ConvertedImage.objects.create(orig=indexedImage, size=t.tell(), metadata=json.dumps({'Type':'preview', 'Width':exifinfo['ImageWidth'], 'GeneratedBy': 'exiftool'}))
        
        t.seek(0)
        prev.file.save('prev', File(t))
        print("Saved {} '{}' as converted image".format('preview', 'exiftool'))
  
  
  
  for conv in indexedImage.getConversions():
    m = json.loads(conv.metadata)
    if m['Type'] == 'preview':
      fd = open(os.path.join(settings.MEDIA_ROOT,conv.file.name), 'r+b')
      print("Using preview image: {}", conv.file.name)
  
  if fd is None:
    fd = open(os.path.realpath(path), 'r+b')
  
  
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
  
  
  detectionsToRun = []
  
  if not rerun:
    for detect in detections:
      runs = DetectionRun.objects.filter(image=indexedImage, detection=get_detection_object(detect))
      
      if runs.count() > 0:
        print("{} detection has already been run".format(detect))
      else:
        print("{} detection can run".format(detect))
        detectionsToRun.append(detect)
  
  
  
  if createdIndexedImage and generateThumbs:
    for tsize in determineThumbsSize(imgWidth):
      with tempfile.SpooledTemporaryFile(max_size=10000000, mode='w+b') as t:
        cpy = img.copy()
        cpy.thumbnail((tsize, tsize))
        cpy.save(t, 'png')
        t.flush()
        thumb = ConvertedImage.objects.create(orig=indexedImage, size=t.tell(), metadata=json.dumps({'Type':'thumbnail', 'Width':tsize}))
        
        t.seek(0)
        thumb.file.save('thumb{}'.format(tsize), File(t))
        print("Saved {} '{}' as converted image".format('thumbnail', tsize))
  
  
  forDetect = ConvertedImage.objects.filter(orig=indexedImage).filter(metadata__iregex=r'"Type": "thumbnail"').filter(size__lte=2000000).order_by("-size")
  forDetect = forDetect[0]
  print("Selected conversion (id={}) for detections: {}".format(forDetect.id, os.path.join(settings.MEDIA_ROOT,forDetect.file.name)))
  
  fd.close()
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
    
    DetectionRun.objects.create(detection=get_detection_object(detect), image=indexedImage)
    
    
    if 'FaceDetails' in res and res['FaceDetails'] is not None:
      for face in res['FaceDetails']:
        detectedFace((img, imgWidth, imgHeight), indexedImage, face, DetectionType.FACE)
        
        if capturePixels:
          bb = calcBB((imgWidth, imgHeight), face['BoundingBox'])
          drawBB(capturePixels, (0,0,255), bb) #BLUE
    
    
    if 'CelebrityFaces' in res:
      for celeb in res['CelebrityFaces']:
        
        (detection, createdDetection) = Detection.objects.get_or_create(type=DetectionType.CELEBRITY)
        
        idet = ImageDetection.objects.create(image=indexedImage, detection=detection, confidence=celeb['MatchConfidence'], identifier=celeb['Name'], metadata=json.dumps(celeb))
        
        face = celeb['Face']
        detectedFace((img, imgWidth, imgHeight), indexedImage, face, DetectionType.CELEBRITY_FACE)
          
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
          print("Saved {} '{}' as detection image".format(text['Type'], text['DetectedText']))
        
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
            print("Saved {} '{}' as detection image".format(DetectionType.LABEL, label['Name']))
          
          if capturePixels:
            drawBB(capturePixels, (255,0,0), bb) #RED
  
  
  if len(detectionsToRun) and imgDetections:
    with tempfile.SpooledTemporaryFile(max_size=10000000, mode='w+b') as t:
      size = determineThumbsSize(imgWidth)[0]
      imgDetections.thumbnail((size, size))
      imgDetections.save(t, 'png')
      t.flush()
      detectionsThumb = ConvertedImage.objects.create(orig=indexedImage,size=t.tell(),metadata=json.dumps({"Type":"detections", "DetectionsInfo":detectionsToRun, "Width": size}))
      t.seek(0)
      detectionsThumb.file.save('dthumb{}'.format(size), File(t))
      print("Saved {} '{}' as converted image".format('detections', detectionsToRun))
  
  
  return indexedImage


