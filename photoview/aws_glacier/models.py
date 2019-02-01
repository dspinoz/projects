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

class Inventory(AWSGlacierModel):
  output = models.TextField(null=True, default=None)
  date = models.DateTimeField(default=datetime.today)

class Job(AWSGlacierModel):
  jobId = models.CharField(max_length=255)
  parameters = models.TextField(blank=True)
  creationDate = models.DateTimeField(default=datetime.today)
  statusCode = models.CharField(max_length=255)
  completionDate = models.DateTimeField(null=True, blank=True, default=None)
  completed = models.BooleanField(default=False)
  description = models.TextField(blank=True)
  action = models.CharField(max_length=255, blank=True)
  snsTopic = models.CharField(max_length=255, null=True, blank=True, default=None)
  retrievedOutput = models.BooleanField(default=False)

class Archive(AWSGlacierModel):
  archiveId = models.CharField(max_length=255)
  size = models.BigIntegerField()
  sha256 = models.CharField(max_length=255, null=True)
  sha256TreeHash = models.CharField(max_length=255)
  description = models.TextField(blank=True)
  creationDate = models.DateTimeField(default=datetime.today)
  deletedDate = models.DateTimeField(null=True, blank=True, default=None)
  partSize = models.BigIntegerField(null=True, blank=True, default=None)

class InventoryRetrieval(models.Model):
  jobId = models.ForeignKey(Job, on_delete=models.CASCADE)
  inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
