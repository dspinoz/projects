# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from datetime import datetime

from django.db import models
from django.dispatch import receiver

# Create your models here.

class AWSGlacierModel(models.Model):
  accountId = models.CharField(max_length=255)
  vaultName = models.CharField(max_length=255)
  class Meta:
    abstract = True

class AWSGlacierRequestResponse(AWSGlacierModel):
  requestId = models.TextField(blank=True)
  lastModifiedDate = models.DateTimeField(auto_now=True)
  date = models.DateTimeField(blank=False, default=datetime.today)
  endpoint = models.TextField(blank=True)
  statusCode = models.IntegerField(default=200)
  retryAttempts = models.IntegerField()
  responseLength = models.IntegerField(default=0)
  responseContentType = models.CharField(max_length=255, blank=True)
  responseBody = models.TextField(blank=True)

class Inventory(AWSGlacierModel):
  output = models.TextField(null=True, default=None)
  date = models.DateTimeField(default=datetime.today)
  processed = models.BooleanField(default=False)
  
  def outputObj(self):
    return json.loads(self.output)

class Job(AWSGlacierModel):
  jobId = models.CharField(max_length=255)
  parameters = models.TextField(blank=True)
  creationDate = models.DateTimeField(default=datetime.today)
  statusCode = models.CharField(max_length=255)
  statusMessage = models.TextField(blank=True)
  completionDate = models.DateTimeField(null=True, blank=True)
  completed = models.BooleanField(default=False)
  description = models.TextField(blank=True)
  action = models.CharField(max_length=255, blank=True)
  snsTopic = models.CharField(max_length=255, null=True, blank=True, default=None)
  retrievedOutput = models.BooleanField(default=False)
  available = models.BooleanField(default=True)
  availableDate = models.DateTimeField(default=datetime.today)
  lastModifiedDate = models.DateTimeField(auto_now=True)
  
  def getChildObject(self):
    return (InventoryRetrieval.objects.filter(job=self.id),
            ArchiveRetrieval.objects.filter(job=self.id))
  
  def hasChildObject(self):
    children = self.getChildObject()
    for c in children:
      if c.count() > 0:
        return True
    return False

class Archive(AWSGlacierModel):
  archiveId = models.CharField(max_length=255)
  size = models.BigIntegerField()
  sha256 = models.CharField(max_length=255, null=True)
  sha256TreeHash = models.CharField(max_length=255)
  description = models.TextField(blank=True)
  creationDate = models.DateTimeField(default=datetime.today)
  deletedDate = models.DateTimeField(null=True, blank=True)
  partSize = models.BigIntegerField(null=True, blank=True, default=None)
  available = models.BooleanField(default=True)
  
  def uploadList(self):
    return ArchiveUpload.objects.filter(archive=self.id)
  
  def retrievalList(self):
    return ArchiveRetrieval.objects.filter(archive=self.id)

class InventoryRetrieval(models.Model):
  job = models.ForeignKey(Job, on_delete=models.CASCADE)
  inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
  lastModifiedDate = models.DateTimeField(auto_now=True)
  vault = models.CharField(max_length=255, default=None)

class ArchiveRetrieval(models.Model):
  job = models.ForeignKey(Job, on_delete=models.CASCADE)
  archive = models.ForeignKey(Archive, on_delete=models.CASCADE)
  lastModifiedDate = models.DateTimeField(auto_now=True)
  startByte = models.BigIntegerField(default=0)
  endByte = models.BigIntegerField(default=0)
  content = models.FileField(upload_to="aws_glc/%Y/%m/%d/", null=True, blank=True, default=None)

class ArchiveUploadRequest(AWSGlacierModel):
  uploadId = models.CharField(max_length=255)
  description = models.TextField(blank=True)
  partSize = models.IntegerField(blank=True)
  filePath = models.TextField()
  size = models.BigIntegerField(default=0)
  sha256 = models.CharField(max_length=255, blank=True)
  sha256TreeHash = models.CharField(max_length=255, blank=True)
  lastModifiedDate = models.DateTimeField(auto_now=True)
  
  def partList(self):
    return ArchiveUploadPart.objects.filter(req=self.id)
  
  def uploadedPartList(self):
    return UploadPart.objects.filter(upload=self.id)

class ArchiveUploadPart(AWSGlacierModel):
  index = models.BigIntegerField(default=0)
  startByte = models.BigIntegerField(default=0)
  endByte = models.BigIntegerField()
  lastModifiedDate = models.DateTimeField(auto_now=True)
  req = models.ForeignKey(ArchiveUploadRequest, on_delete=models.CASCADE, default=None, null=True)
  
  def isUploaded(self):
    return self.getUpload().count > 0
  
  def getUpload(self):
    return UploadPart.objects.filter(part=self.id)

class UploadPart(models.Model):
  upload = models.ForeignKey(ArchiveUploadRequest, on_delete=models.CASCADE)
  part = models.ForeignKey(ArchiveUploadPart, on_delete=models.CASCADE)
  sha256 = models.CharField(max_length=255)
  lastModifiedDate = models.DateTimeField(auto_now=True)

class ArchiveUpload(models.Model):
  upload = models.ForeignKey(ArchiveUploadRequest, on_delete=models.CASCADE)
  archive = models.ForeignKey(Archive, on_delete=models.CASCADE)
  lastModifiedDate = models.DateTimeField(auto_now=True)

@receiver(models.signals.post_delete, sender=ArchiveRetrieval)
def auto_delete_file_on_delete(sender, instance, **kwargs):
  """
  Deletes file from filesystem when corresponding object is deleted.
  """
  if instance.content:
    if os.path.isfile(instance.content.path):
      if os.path.isfile(instance.content.path):
        os.remove(instance.content.path)
