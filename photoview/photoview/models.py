# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
from datetime import datetime

from django.db import models
from django.dispatch import receiver

# TODO: do not import this package! check usages
import aws_rekognition

# Create your models here.

class IndexedImage(models.Model):
  filePath = models.TextField()
  sha256 = models.CharField(max_length=255)
  width = models.IntegerField()
  height = models.IntegerField()
  size = models.BigIntegerField()
  contentType = models.CharField(max_length=255)
  metadata = models.TextField(blank=True, default=None, null=True)
  creationDate = models.DateTimeField(default=datetime.today)
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


class ConvertedImage(models.Model):
  orig = models.ForeignKey(IndexedImage, models.CASCADE)
  file = models.ImageField(upload_to='photoview/%Y/%m/%d/')
  size = models.BigIntegerField()
  metadata = models.TextField(blank=True, default=None, null=True)
  creationDate = models.DateTimeField(default=datetime.today)
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
