# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
from datetime import datetime

from django.db import models
from django.dispatch import receiver

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
