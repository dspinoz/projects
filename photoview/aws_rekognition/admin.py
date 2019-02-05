# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from .models import AWSRekognitionRequestResponse

@admin.register(AWSRekognitionRequestResponse)
class AWSRekognitionRequestResponseAdmin(admin.ModelAdmin):
  date_hierarchy = 'date'
  list_display = ('id', 'requestId', 'endpoint', 'statusCode', 'retryAttempts', 'responseContentType', 'responseLength')
  list_filter = ('date', 'endpoint', 'statusCode', 'responseContentType')
