# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from enum import Enum
from datetime import datetime

from django.db import models
from django.dispatch import receiver

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

class IndexedImage(models.Model):
  filePath = models.TextField()
  sha256 = models.CharField(max_length=255)
  width = models.IntegerField()
  height = models.IntegerField()
  contentType = models.CharField(max_length=255)
  metadata = models.TextField(blank=True, default=None, null=True)
  creationDate = models.DateTimeField(default=datetime.today)
  lastModifiedDate = models.DateTimeField(auto_now=True)

class ConvertedImage(models.Model):
  orig = models.ForeignKey(IndexedImage, models.CASCADE)
  file = models.ImageField(upload_to='uploads/%Y/%m/%d/')
  metadata = models.TextField(blank=True, default=None, null=True)
  creationDate = models.DateTimeField(default=datetime.today)
  lastModifiedDate = models.DateTimeField(auto_now=True)

@receiver(models.signals.post_delete, sender=ConvertedImage)
def auto_delete_file_on_delete(sender, instance, **kwargs):
  """
  Deletes file from filesystem
  when corresponding `ConvertedImage` object is deleted.
  """
  if instance.file:
    if os.path.isfile(instance.file.path):
      instance.file.delete()

@receiver(models.signals.pre_save, sender=ConvertedImage)
def auto_delete_file_on_change(sender, instance, **kwargs):
  """
  Deletes old file from filesystem
  when corresponding `ConvertedImage` object is updated
  with new file.
  """
  if not instance.pk:
    return False

  try:
    old_file = ConvertedImage.objects.get(pk=instance.pk).file
  except ConvertedImage.DoesNotExist:
    return False
  try:
    new_file = instance.file
    if not old_file == new_file:
      if os.path.isfile(old_file.path):
        os.remove(old_file.path)
  except ValueError:
    return False

class DetectionType(Enum):
  FACE = "FACE"
  LABEL = "LABEL"
  TEXT_WORD = "TEXT_WORD"
  TEXT_LINE = "TEXT_LINE"
  CELEBRITY = "FACE_CELEBRITY"
  LANDMARK = "FACE_LANDMARK"
  FACE_UNKNOWN = "FACE_UNKNOWN"
  UNKNOWN = "UNKNOWN"

class Detection(models.Model):
  type = models.CharField(max_length=15, choices=[(tag, tag.value) for tag in DetectionType])
  creationDate = models.DateTimeField(default=datetime.today)
  lastModifiedDate = models.DateTimeField(auto_now=True)

class ImageDetection(models.Model):
  image = models.ForeignKey(IndexedImage, on_delete=models.CASCADE)
  detection = models.ForeignKey(Detection, on_delete=models.CASCADE)
  file = models.ImageField(upload_to='uploads/%Y/%m/%d/')
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
  Deletes file from filesystem
  when corresponding `ImageDetection` object is deleted.
  """
  if instance.file:
    if os.path.isfile(instance.file.path):
      instance.file.delete()

@receiver(models.signals.pre_save, sender=ImageDetection)
def auto_delete_file_on_change(sender, instance, **kwargs):
  """
  Deletes old file from filesystem
  when corresponding `ImageDetection` object is updated
  with new file.
  """
  if not instance.pk:
    return False

  try:
    old_file = ImageDetection.objects.get(pk=instance.pk).file
  except ImageDetection.DoesNotExist:
    return False
  try:
    new_file = instance.file
    if not old_file == new_file:
      if os.path.isfile(old_file.path):
        os.remove(old_file.path)
  except ValueError:
    return False