from datetime import datetime
import dateutil
import json
import os
import mimetypes
import sys
import hashlib

from django.core.files import File
from django.conf import settings

from photoview.models import IndexedImage, ConvertedImage, DelayedCompute, DelayedComputeType
import photoview.utils

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
    print("Image already indexed, {}", indexedImage.id)
  except IndexedImage.DoesNotExist:
    
    st = os.stat(os.path.realpath(path))
    
    hash_compute = DelayedCompute.objects.create(image=indexedImage, type=DelayedComputeType.CHECKSUM, metadata=json.dumps({'path': os.path.realpath(path)}))
    exif_compute = DelayedCompute.objects.create(image=indexedImage, type=DelayedComputeType.EXIF_METADATA, metadata=json.dumps({'path':os.path.realpath(path)}))
    
    hash_compute.next_compute = exif_compute
    hash_compute.save()
    
    hexdigest = hash_compute.run()
    exifmeta = json.loads(exif_compute.metadata)
    exifinfo = exifmeta['result']
    exifdate = exifmeta['date']
    
    
    
    # TODO move mimetype to compute
    mt = mimetypes.guess_type(path)
    ftype = mt[0]
    
    if ftype is None:
      raise Exception("Unidentified image type {}".format(path))
    
    saveType = 'JPEG'
    if mt[0] == 'image/png':
      saveType = 'PNG'
    
    indexedImage = IndexedImage.objects.create(filePath=os.path.realpath(path), sha256=hexdigest, creationDate=exifdate, width=exifinfo['ImageWidth'], height=exifinfo['ImageHeight'], contentType=ftype, size=st.st_size, metadata=json.dumps(exifinfo))
    createdIndexedImage = True
    
    for c in [exif_compute, hash_compute]:
      c.image = indexedImage
      c.save()
    
    prev_compute = DelayedCompute.objects.create(image=indexedImage, type=DelayedComputeType.PREVIEW, metadata=json.dumps({'previewType':saveType, 'width': exifinfo['ImageWidth']}))
    prev_compute.run()
    
    
    img = indexedImage.getImg()
    
    
    orient_compute = DelayedCompute.objects.create(image=indexedImage, type=DelayedComputeType.ORIENTATION, metadata=json.dumps({'previewType':saveType}))
    orient_compute.run()
    
    
    imgBB = img.getbbox()
    imgWidth = imgBB[2] - imgBB[0]
    
    for tsize in photoview.utils.determineThumbsSize(imgWidth):
      thumb_compute = DelayedCompute.objects.create(image=indexedImage, type=DelayedComputeType.THUMBNAIL, metadata=json.dumps({'thumbType':saveType, 'width': tsize}))
      thumb_compute.run()
  
  return (indexedImage,createdIndexedImage)
  
