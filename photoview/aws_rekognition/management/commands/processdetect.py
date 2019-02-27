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

from photoview.models import IndexedImage, ConvertedImage

from aws_rekognition.models import AWSRekognitionRequestResponse
from aws_rekognition.models import DetectionType, Detection, ImageDetection

import aws_rekognition.utils as u

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
{"FaceDetails": [{"BoundingBox": {"Width": 0.08800298720598221, "Top": 0.3465072512626648, "Left": 0.4096584618091583, "Height": 0.06927412003278732}, "Landmarks": [{"Y": 0.3783688545227051, "X": 0.44486063718795776, "Type": "eyeLeft"}, {"Y": 0.37806645035743713, "X": 0.48226675391197205, "Type": "eyeRight"}, {"Y": 0.4027611017227173, "X": 0.4484062194824219, "Type": "mouthLeft"}, {"Y": 0.4024704694747925, "X": 0.47947585582733154, "Type": "mouthRight"}, {"Y": 0.3901897072792053, "X": 0.4663908779621124, "Type": "nose"}], "Pose": {"Yaw": -2.440105676651001, "Roll": -6.147082805633545, "Pitch": 32.27157211303711}, "Quality": {"Sharpness": 32.20803451538086, "Brightness": 67.85246276855469}, "Confidence": 99.99993896484375}], "ResponseMetadata": {"RetryAttempts": 0, "HTTPStatusCode": 200, "RequestId": "cda60f5c-29f1-11e9-a14b-43d1b7eee780", "HTTPHeaders": {"date": "Wed, 06 Feb 2019 09:30:47 GMT", "x-amzn-requestid": "cda60f5c-29f1-11e9-a14b-43d1b7eee780", "content-length": "679", "content-type": "application/x-amz-json-1.1", "connection": "keep-alive"}}}
        """)
      elif detect == 'labels':
        res = json.loads("""
{"Labels": [{"Instances": [], "Confidence": 99.65349578857422, "Parents": [], "Name": "Apparel"}, {"Instances": [], "Confidence": 99.65349578857422, "Parents": [], "Name": "Clothing"}, {"Instances": [], "Confidence": 98.15912628173828, "Parents": [{"Name": "Clothing"}], "Name": "Sleeve"}, {"Instances": [{"BoundingBox": {"Width": 0.21388906240463257, "Top": 0.22503480315208435, "Left": 0.3488169014453888, "Height": 0.6210546493530273}, "Confidence": 97.92111206054688}], "Confidence": 97.92111206054688, "Parents": [], "Name": "Person"}, {"Instances": [], "Confidence": 97.92111206054688, "Parents": [], "Name": "Human"}, {"Instances": [], "Confidence": 92.56321716308594, "Parents": [{"Name": "Plant"}], "Name": "Tree"}, {"Instances": [], "Confidence": 92.56321716308594, "Parents": [], "Name": "Plant"}, {"Instances": [], "Confidence": 91.517333984375, "Parents": [{"Name": "Clothing"}], "Name": "Shorts"}, {"Instances": [], "Confidence": 82.3343276977539, "Parents": [{"Name": "Sleeve"}, {"Name": "Clothing"}], "Name": "Long Sleeve"}, {"Instances": [], "Confidence": 69.0826187133789, "Parents": [], "Name": "Wood"}, {"Instances": [], "Confidence": 63.48865509033203, "Parents": [{"Name": "Light"}], "Name": "Flare"}, {"Instances": [], "Confidence": 63.48865509033203, "Parents": [], "Name": "Light"}, {"Instances": [], "Confidence": 62.53249740600586, "Parents": [{"Name": "Tree"}, {"Name": "Plant"}], "Name": "Tree Trunk"}, {"Instances": [], "Confidence": 60.64990997314453, "Parents": [{"Name": "Person"}], "Name": "Female"}, {"Instances": [], "Confidence": 60.64990997314453, "Parents": [{"Name": "Person"}, {"Name": "Female"}], "Name": "Girl"}, {"Instances": [], "Confidence": 59.13471984863281, "Parents": [{"Name": "Tree"}, {"Name": "Plant"}], "Name": "Abies"}, {"Instances": [], "Confidence": 59.13471984863281, "Parents": [{"Name": "Tree"}, {"Name": "Plant"}], "Name": "Fir"}, {"Instances": [], "Confidence": 57.4941520690918, "Parents": [], "Name": "Ground"}, {"Instances": [], "Confidence": 56.87697982788086, "Parents": [{"Name": "Clothing"}], "Name": "Footwear"}, {"Instances": [{"BoundingBox": {"Width": 0.05898282304406166, "Top": 0.78066086769104, "Left": 0.39639145135879517, "Height": 0.05759739875793457}, "Confidence": 56.87697982788086}], "Confidence": 56.87697982788086, "Parents": [{"Name": "Footwear"}, {"Name": "Clothing"}], "Name": "Shoe"}, {"Instances": [], "Confidence": 55.39082336425781, "Parents": [{"Name": "Person"}, {"Name": "Sport"}], "Name": "Working Out"}, {"Instances": [], "Confidence": 55.39082336425781, "Parents": [{"Name": "Person"}, {"Name": "Sport"}], "Name": "Exercise"}, {"Instances": [], "Confidence": 55.39082336425781, "Parents": [{"Name": "Person"}], "Name": "Sports"}, {"Instances": [], "Confidence": 55.39082336425781, "Parents": [{"Name": "Person"}], "Name": "Sport"}], "ResponseMetadata": {"RetryAttempts": 0, "HTTPStatusCode": 200, "RequestId": "02e865a9-29f2-11e9-b6ee-fd78b2e84870", "HTTPHeaders": {"date": "Wed, 06 Feb 2019 09:32:15 GMT", "x-amzn-requestid": "02e865a9-29f2-11e9-b6ee-fd78b2e84870", "content-length": "2611", "content-type": "application/x-amz-json-1.1", "connection": "keep-alive"}}, "LabelModelVersion": "2.0"}
        """)
      elif detect == 'text':
        res = json.loads("""
{"TextDetections": [], "ResponseMetadata": {"RetryAttempts": 0, "HTTPStatusCode": 200, "RequestId": "ea30bb24-29f1-11e9-a14b-43d1b7eee780", "HTTPHeaders": {"date": "Wed, 06 Feb 2019 09:31:32 GMT", "x-amzn-requestid": "ea30bb24-29f1-11e9-a14b-43d1b7eee780", "content-length": "21", "content-type": "application/x-amz-json-1.1", "connection": "keep-alive"}}}
        """)
      elif detect == 'celebrities':
        res = json.loads("""
{"UnrecognizedFaces": [{"BoundingBox": {"Width": 0.10496719926595688, "Top": 0.34812501072883606, "Left": 0.40862229466438293, "Height": 0.07000000029802322}, "Confidence": 99.9653549194336, "Pose": {"Yaw": 3.490149736404419, "Roll": -0.2914309799671173, "Pitch": 7.869302272796631}, "Quality": {"Sharpness": 89.91268920898438, "Brightness": 81.41223907470703}, "Landmarks": [{"Y": 0.3777780532836914, "X": 0.44560757279396057, "Type": "eyeLeft"}, {"Y": 0.37788867950439453, "X": 0.4832105338573456, "Type": "eyeRight"}, {"Y": 0.38782942295074463, "X": 0.4648663401603699, "Type": "nose"}, {"Y": 0.4009677469730377, "X": 0.44392716884613037, "Type": "mouthLeft"}, {"Y": 0.400946706533432, "X": 0.4819994866847992, "Type": "mouthRight"}]}, {"BoundingBox": {"Width": 0.02624179981648922, "Top": 0.4300000071525574, "Left": 0.6335520148277283, "Height": 0.017500000074505806}, "Confidence": 94.85904693603516, "Pose": {"Yaw": -11.95541763305664, "Roll": 1.454291820526123, "Pitch": 9.053011894226074}, "Quality": {"Sharpness": 4.397488594055176, "Brightness": 66.41490936279297}, "Landmarks": [{"Y": 0.43761399388313293, "X": 0.6421526074409485, "Type": "eyeLeft"}, {"Y": 0.4377366602420807, "X": 0.6499112248420715, "Type": "eyeRight"}, {"Y": 0.44106510281562805, "X": 0.6445012092590332, "Type": "nose"}, {"Y": 0.4445219337940216, "X": 0.6434136629104614, "Type": "mouthLeft"}, {"Y": 0.4449247717857361, "X": 0.6485344171524048, "Type": "mouthRight"}]}], "CelebrityFaces": [], "ResponseMetadata": {"RetryAttempts": 0, "HTTPStatusCode": 200, "RequestId": "4e522014-29f2-11e9-b6ee-fd78b2e84870", "HTTPHeaders": {"date": "Wed, 06 Feb 2019 09:34:23 GMT", "x-amzn-requestid": "4e522014-29f2-11e9-b6ee-fd78b2e84870", "content-length": "1400", "content-type": "application/x-amz-json-1.1", "connection": "keep-alive"}}, "OrientationCorrection": "ROTATE_0"}
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
