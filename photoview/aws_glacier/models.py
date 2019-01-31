# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class AWSGlacierModel(models.Model):
  accountId = models.CharField(max_length=255)
  vaultName = models.CharField(max_length=255)

class Inventory(AWSGlacierModel):
  output = models.TextField()
  date = models.DateTimeField()
  
