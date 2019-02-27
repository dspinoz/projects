# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json

from enum import Enum
from datetime import datetime

from django.db import models
from django.dispatch import receiver

from photoview.models import IndexedImage
from photoview.models import ConvertedImage

# Create your models here.

class AWSRekognitionRequestResponse(models.Model):
  requestId = models.TextField(blank=True)
  lastModifiedDate = models.DateTimeField(auto_now=True)
  date = models.DateTimeField(blank=False, default=datetime.today)
  endpoint = models.TextField(blank=True)
  statusCode = models.IntegerField(default=200)
  retryAttempts = models.IntegerField()
  responseLength = models.IntegerField(default=0)
  responseContentType = models.CharField(max_length=255, blank=True)
  responseBody = models.TextField(blank=True)

class DetectionType(Enum):
  FACE = "FACE"
  LABEL = "LABEL"
  TEXT_WORD = "TEXT_WORD"
  TEXT_LINE = "TEXT_LINE"
  TEXT_ANY = "TEXT"
  CELEBRITY = "CELEBRITY"
  CELEBRITY_FACE = "FACE_CELEBRITY"
  LANDMARK = "FACE_LANDMARK"
  FACE_UNKNOWN = "FACE_UNKNOWN"
  UNKNOWN = "UNKNOWN"

class Detection(models.Model):
  type = models.CharField(max_length=15, choices=[(tag, tag.value) for tag in DetectionType])
  creationDate = models.DateTimeField(default=datetime.today)
  lastModifiedDate = models.DateTimeField(auto_now=True)
  
  def typeShort(self):
    return self.type.split('.')[1]

class DetectionRun(models.Model):
  image = models.ForeignKey(IndexedImage, on_delete=models.CASCADE)
  detection = models.ForeignKey(Detection, on_delete=models.CASCADE)
  lastModifiedDate = models.DateTimeField(auto_now=True)

class ImageDetection(models.Model):
  image = models.ForeignKey(IndexedImage, on_delete=models.CASCADE)
  detection = models.ForeignKey(Detection, on_delete=models.CASCADE)
  file = models.ImageField(upload_to='aws_rek/%Y/%m/%d/')
  confidence = models.FloatField(default=0.0)
  identifier = models.TextField(blank=True, null=True, default=None)
  boundingBoxTop = models.FloatField(blank=True, null=True, default=None)
  boundingBoxLeft = models.FloatField(blank=True, null=True, default=None)
  boundingBoxWidth = models.FloatField(blank=True, null=True, default=None)
  boundingBoxHeight = models.FloatField(blank=True, null=True, default=None)
  metadata = models.TextField(blank=True, default=None, null=True)
  creationDate = models.DateTimeField(default=datetime.today)
  lastModifiedDate = models.DateTimeField(auto_now=True)

@receiver(models.signals.post_delete, sender=ImageDetection)
def auto_delete_file_on_delete(sender, instance, **kwargs):
  """
  Deletes file from filesystem when corresponding object is deleted.
  """
  if instance.file:
    if os.path.isfile(instance.file.path):
      if os.path.isfile(instance.file.path):
        os.remove(instance.file.path)
