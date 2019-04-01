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
from PIL import Image, ExifTags

from django.core.files import File
from django.conf import settings

from photoview.models import IndexedImage, ConvertedImage
from photoview.models import IndexedImage, ConvertedImage, DelayedCompute, DelayedComputeType

def determineThumbsSize(width):
  sizes = []
  sz = width
  while sz > 20: #dont go smaller than 16 pixels, too small to see anything useful!
    sizes.append(sz)
    sz = sz/2
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
  
def getIndexedImage(path, hasher=hashlib.sha256(), generateThumbs=True, runExifTool=True, convertUnknownImages=True):
  createdIndexedImage = False
  indexedImage = None
  try:
    indexedImage = IndexedImage.objects.get(filePath=os.path.realpath(path))
    print("Image already indexed")
  except IndexedImage.DoesNotExist:
    
    hash_compute = DelayedCompute.objects.create(image=indexedImage, type=DelayedComputeType.CHECKSUM, metadata=json.dumps({'path': os.path.realpath(path)}))
    hexdigest = hash_compute.run()
    
    exif_compute = DelayedCompute.objects.create(image=indexedImage, type=DelayedComputeType.EXIF_METADATA, metadata=json.dumps({'path':os.path.realpath(path)}))
    exifinfo = json.loads(exif_compute.run())
    exifdate = json.loads(exif_compute.metadata)['date']
    
    indexedImage = IndexedImage.objects.create(filePath=os.path.realpath(path), sha256=hexdigest, creationDate=exifdate, width=exifinfo['ImageWidth'], height=exifinfo['ImageHeight'], contentType=mimetypes.guess_type(path)[0], size=fd.tell(), metadata=json.dumps(exifinfo))
    createdIndexedImage = True
    
    for c in [exif_compute, hash_compute]:
      c.image = indexedImage
      c.save()
    
    prev_compute = DelayedCompute.objects.create(image=indexedImage, type=DelayedComputeType.PREVIEW, metadata=json.dumps({'previewType':'JPEG', 'width': exifinfo['ImageWidth']}))
    prev_compute.run()
    
    
    img = indexedImage.getImg()
    
    
    orient_compute = DelayedCompute.objects.create(image=indexedImage, type=DelayedComputeType.ORIENTATION, metadata=json.dumps({'previewType':'JPEG'}))
    orient_compute.run()
    
    
    imgBB = img.getbbox()
    imgWidth = imgBB[2] - imgBB[0]
    
    for tsize in photoview.utils.determineThumbsSize(imgWidth):
      thumb_compute = DelayedCompute.objects.create(image=indexedImage, type=DelayedComputeType.THUMBNAIL, metadata=json.dumps({'thumbType':'JPEG', 'width': tsize}))
      thumb_compute.run()
  
  return (indexedImage,createdIndexedImage)
  
