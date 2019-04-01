# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
import datetime
from enum import Enum
import hashlib
import subprocess
import tempfile

from django.db import models
from django.dispatch import receiver
from django.core.files import File

# TODO: do not import this package! check usages
import aws_rekognition
from PIL import Image, ExifTags

# util functions

def defaultDateTime(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

# Create your models here.

class IndexedImage(models.Model):
  filePath = models.TextField()
  sha256 = models.CharField(max_length=255)
  width = models.IntegerField()
  height = models.IntegerField()
  size = models.BigIntegerField()
  contentType = models.CharField(max_length=255)
  metadata = models.TextField(blank=True, default=None, null=True)
  creationDate = models.DateTimeField(default=datetime.datetime.today)
  lastModifiedDate = models.DateTimeField(auto_now=True)
  
  def fileName(self):
    return os.path.basename(self.filePath)
    
  def getConversions(self):
    return ConvertedImage.objects.filter(orig=self.id)
  
  
  def determineThumbsSize(self, width):
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
  
  def getConversion(self, size):
    qs = ConvertedImage.objects.filter(orig=self.id).filter(metadata__iregex=r'"Type": "thumbnail"')
    sizes = self.determineThumbsSize(int(size))
    for s in sizes:
      match = qs.filter(metadata__iregex=r'"Width": {}'.format(s))
      if match.count():
        return match[0]
    return None
    
  # TODO: Fix circular dependency between photoview and aws_rekognition!
  def getDetections(self):
    return aws_rekognition.models.ImageDetection.objects.filter(image=self.id).order_by('-confidence')
    
  def getPreviewPath(self):
    for conv in self.getConversions():
      m = json.loads(conv.metadata)
      if m['Type'] == 'preview':
        return os.path.join(settings.MEDIA_ROOT,conv.file.name)
    return None
    
  def getImg(self):
    if hasattr(self,'img') and self.img is not None:
      print("Loaded cached image: {} {}", self.id, self.img)
      return self.img
    
    #TODO what if orientation has been performed!?
    prev = self.getPreviewPath()
    if prev:
      fd = open(prev, 'r+b')
      print("Loading preview image: {} {}", self.id, prev)
    else:
      fd = open(self.filePath, 'r+b')
      print("Loading image: {}", self.id)
    
    self.img = Image.open(fd)
    
    cpy = self.img.copy()
    
    fd.close()
    
    self.img = cpy
    
    return self.img
    

class ConvertedImage(models.Model):
  orig = models.ForeignKey(IndexedImage, models.CASCADE)
  file = models.ImageField(upload_to='photoview/%Y/%m/%d/')
  size = models.BigIntegerField()
  metadata = models.TextField(blank=True, default=None, null=True)
  creationDate = models.DateTimeField(default=datetime.datetime.today)
  lastModifiedDate = models.DateTimeField(auto_now=True)
  
  def metadataObj(self):
    if self.metadata:
      return json.loads(self.metadata)
    return None
    
  def getImageCreationDate(self):
    img = IndexedImage.objects.get(id=self.orig.id)
    return img.creationDate

@receiver(models.signals.post_delete, sender=ConvertedImage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
  """
  Deletes file from filesystem when corresponding object is deleted.
  """
  if instance.file:
    if os.path.isfile(instance.file.path):
      if os.path.isfile(instance.file.path):
        os.remove(instance.file.path)

class DelayedComputeType(Enum):
  PREVIEW = "prev"
  THUMBNAIL = "thu"
  EXIF_METADATA = "exif"
  ORIENTATION = "orit"
  CHECKSUM = "hash"
  UNKNOWN = "UNKNOWN"
  
class DelayedCompute(models.Model):
  image = models.ForeignKey(IndexedImage, models.CASCADE, null=True, blank=True, default=None)
  type = models.CharField(max_length=4, choices=[(tag, tag.value) for tag in DelayedComputeType])
  metadata = models.TextField(blank=True, default=None, null=True)
  creationDate = models.DateTimeField(default=datetime.datetime.today)
  completionDate = models.DateTimeField(null=True, blank=True)
  lastModifiedDate = models.DateTimeField(auto_now=True)

  def run(self):
    retval = None
    meta = json.loads(self.metadata)

    if self.type == DelayedComputeType.CHECKSUM:
      meta['type'] = 'sha256'
      hasher = hashlib.sha256()
      fd = open(meta['path'])
      while True:
        b = fd.read()
        if not b:
          break
        hasher.update(b"".join(b))
      retval = hasher.hexdigest()
   
    elif self.type == DelayedComputeType.EXIF_METADATA:
      
      exifinfostr = subprocess.Popen("exiftool -d '%a, %d %b %Y %H:%M:%S %Z' -j '{}'".format(os.path.realpath(meta['path'])), shell=True, stdout=subprocess.PIPE).stdout.read()
      if len(exifinfostr) == 0:
        meta['error'] = "Could not generate exif metadata from {}".format(meta['path'])
      else:
        exifinfo = json.loads(exifinfostr)[0]
        
        if 'Error' in exifinfo:
          meta['error'] = exifinfo['Error']
        
        retval = json.dumps(exifinfo)
      
        meta['date'] = datetime.datetime.today()
        try:
          meta['date'] = dateutil.parser.parse(exifinfo['DateTimeOriginal'])
        except:
          try:
            meta['date'] = dateutil.parser.parse(exifinfo['ProfileDateTime'])
          except:
            pass
    
    elif self.type == DelayedComputeType.PREVIEW:
    
      previewImageBytes = subprocess.Popen("exiftool -Composite:PreviewImage -b '{}'".format(os.path.realpath(self.image.filePath)), shell=True, stdout=subprocess.PIPE).stdout.read()
      if len(previewImageBytes) > 0:
        with tempfile.NamedTemporaryFile(mode='w+b', suffix=".{}".format(meta['previewType'])) as t:
          t.write(previewImageBytes)
          t.flush()
          
          prev = ConvertedImage.objects.create(orig=self.image, size=t.tell(), metadata=json.dumps({'Type':'preview', 'Width':meta['width'], 'GeneratedBy': 'exiftool', 'FileType': meta['previewType']}))
          
          t.seek(0)
          prev.file.save('prev', File(t))
          print("Saved {} '{}' as converted image".format('preview', 'exiftool'))
          
          meta['message'] = 'Successfully generated preview image'
          meta['convertedImage'] = prev.id
          retval = True
      else:
        meta['message'] = 'No preview image available'
        retval = False
    
    elif self.type == DelayedComputeType.ORIENTATION:
      img = self.image.getImg()
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
        
        with tempfile.NamedTemporaryFile(mode='w+b', suffix=".{}".format(meta['previewType'])) as t:
          rot = img.copy();
          rot.save(t, meta['previewType'])
          t.flush()
          
          prev = ConvertedImage.objects.create(orig=self.image, size=t.tell(), metadata=json.dumps({'Type':'preview', 'Width':exifinfo['ImageWidth'], 'GeneratedBy': 'orientation', 'FileType': meta['previewType']}))
          
          t.seek(0)
          prev.file.save('prev', File(t))
          meta['message'] = "Saved {} '{}' as converted image".format('preview', 'orientation')
          retval = True
          
      except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        meta['message'] = "No getexif for {}".format(self.image.id)
        retval = False
    
    elif self.type == DelayedComputeType.THUMBNAIL:
      img = self.image.getImg()
      with tempfile.SpooledTemporaryFile(max_size=10000000, mode='w+b') as t:
        cpy = img.copy()
        cpy.thumbnail((meta['width'], meta['width']))
        cpy.save(t, meta['thumbType'])
        t.flush()
        thumb = ConvertedImage.objects.create(orig=self.image, size=t.tell(), metadata=json.dumps({'Type':'thumbnail', 'Width':meta['width'], 'FileType': meta['thumbType']}))
        
        t.seek(0)
        thumb.file.save('thumb{}'.format(meta['width']), File(t))
        meta['message'] = "Saved {} '{}' as converted image".format('thumbnail', meta['width'])
        retval = True
      
      
    meta['result'] = retval
    
    self.metadata = json.dumps(meta, default=defaultDateTime)
    self.completionDate = datetime.datetime.today()
    self.save()

    return retval


