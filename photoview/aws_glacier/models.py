# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.db import models

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
  responseContentType = models.CharField(max_length=255)
  responseBody = models.TextField(blank=True)

class Inventory(AWSGlacierModel):
  output = models.TextField(null=True, default=None)
  date = models.DateTimeField(default=datetime.today)

class Job(AWSGlacierModel):
  jobId = models.CharField(max_length=255)
  parameters = models.TextField(blank=True)
  creationDate = models.DateTimeField(default=datetime.today)
  statusCode = models.CharField(max_length=255)
  completionDate = models.DateTimeField(null=True, blank=True)
  completed = models.BooleanField(default=False)
  description = models.TextField(blank=True)
  action = models.CharField(max_length=255, blank=True)
  snsTopic = models.CharField(max_length=255, null=True, blank=True, default=None)
  retrievedOutput = models.BooleanField(default=False)
  available = models.BooleanField(default=True)
  availableDate = models.DateTimeField(default=datetime.today)
  lastModifiedDate = models.DateTimeField(auto_now=True)

class Archive(AWSGlacierModel):
  archiveId = models.CharField(max_length=255)
  size = models.BigIntegerField()
  sha256 = models.CharField(max_length=255, null=True)
  sha256TreeHash = models.CharField(max_length=255)
  description = models.TextField(blank=True)
  creationDate = models.DateTimeField(default=datetime.today)
  deletedDate = models.DateTimeField(null=True, blank=True)
  partSize = models.BigIntegerField(null=True, blank=True, default=None)

class InventoryRetrieval(models.Model):
  job = models.ForeignKey(Job, on_delete=models.CASCADE)
  inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
  lastModifiedDate = models.DateTimeField(auto_now=True)
  vault = models.CharField(max_length=255, default=None)
