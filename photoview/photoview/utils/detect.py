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
    
    fd = open(os.path.realpath(path), 'r+b')
    
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
    
    
    for conv in indexedImage.getConversions():
      m = json.loads(conv.metadata)
      if m['Type'] == 'preview':
        fd.close()
        fd = open(os.path.join(settings.MEDIA_ROOT,conv.file.name), 'r+b')
        print("Using preview image: {}", conv.file.name)
    
    
    fd.seek(0)
    img = Image.open(fd)
    imgBB = img.getbbox()
    imgWidth = imgBB[2] - imgBB[0]
    
    
    try:
      for orientation in ExifTags.TAGS.keys():
          if ExifTags.TAGS[orientation]=='Orientation':
              break
      exif=dict(img._getexif().items())

      if exif[orientation] == 3:
        img=img.rotate(180, expand=True)
      elif exif[orientation] == 6:
        img=img.rotate(270, expand=True)
      elif exif[orientation] == 8:
        img=img.rotate(90, expand=True)
        
      orient_compute = DelayedCompute.objects.create(image=indexedImage, type=DelayedComputeType.ORIENTATION)
      
      previewType = 'JPEG'
      with tempfile.NamedTemporaryFile(mode='w+b', suffix=".{}".format(previewType)) as t:
        rot = img.copy();
        rot.save(t, previewType)
        t.flush()
        
        prev = ConvertedImage.objects.create(orig=indexedImage, size=t.tell(), metadata=json.dumps({'Type':'preview', 'Width':exifinfo['ImageWidth'], 'GeneratedBy': 'orientation', 'FileType': previewType}))
        
        t.seek(0)
        prev.file.save('prev', File(t))
        print("Saved {} '{}' as converted image".format('preview', 'orientation'))
        
      orient_compute.completionDate = datetime.today()
      orient_compute.save()
    except (AttributeError, KeyError, IndexError):
      # cases: image don't have getexif
      pass
    
    
    if generateThumbs:
      thumbType = 'JPEG' # or 'png'
      if createdIndexedImage and generateThumbs:
        for tsize in determineThumbsSize(imgWidth):
          thumb_compute = DelayedCompute.objects.create(image=indexedImage, type=DelayedComputeType.THUMBNAIL)
          with tempfile.SpooledTemporaryFile(max_size=10000000, mode='w+b') as t:
            cpy = img.copy()
            cpy.thumbnail((tsize, tsize))
            cpy.save(t, thumbType)
            t.flush()
            thumb = ConvertedImage.objects.create(orig=indexedImage, size=t.tell(), metadata=json.dumps({'Type':'thumbnail', 'Width':tsize, 'FileType': thumbType}))
            
            t.seek(0)
            thumb.file.save('thumb{}'.format(tsize), File(t))
            print("Saved {} '{}' as converted image".format('thumbnail', tsize))
          thumb_compute.metadata = json.dumps({'Message': 'Successfully saved thumbnail', 'Width': tsize, 'FileType': thumbType})
          thumb_compute.completionDate = datetime.today()
          thumb_compute.save()
    
    fd.close()
  
  return (indexedImage,createdIndexedImage)
  
