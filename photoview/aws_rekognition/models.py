# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from django.db import models

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
