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
    
    hash_compute.next_computes.add(exif_compute)
    
    #hash_compute.save()
    exif_compute.save()
    
    hexdigest = hash_compute.run()
    #exif_compute.run()
    exifmeta = json.loads(exif_compute.metadata)
    print("META",exifmeta)
    exifinfo = exifmeta['result']
    exifdate = exifmeta['date']
    
    print("hex",hexdigest,"exifdate", exifdate, "exifinfo",exifinfo)
    print("width",exifinfo['ImageWidth'])
    
    
    
    # TODO move mimetype to compute
    mt = mimetypes.guess_type(path)
    print("MIME",mt)
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
  
