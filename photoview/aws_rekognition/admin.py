# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from .models import AWSRekognitionRequestResponse
from .models import ConvertedImage
from .models import IndexedImage
from .models import Detection
from .models import ImageDetection

@admin.register(AWSRekognitionRequestResponse)
class AWSRekognitionRequestResponseAdmin(admin.ModelAdmin):
  date_hierarchy = 'date'
  list_display = ('id', 'requestId', 'endpoint', 'statusCode', 'retryAttempts', 'responseContentType', 'responseLength')
  list_filter = ('date', 'endpoint', 'statusCode', 'responseContentType')

class ConvertedImageInline(admin.TabularInline):
  model = ConvertedImage

class ImageDetectionInline(admin.TabularInline):
  model = ImageDetection

@admin.register(IndexedImage)
class IndexedImageAdmin(admin.ModelAdmin):
  date_hierarchy = 'creationDate'
  list_display = ('id','filePath', 'width', 'height', 'contentType')
  list_filter = ('contentType', 'width', 'height')
  inlines = [ConvertedImageInline, ImageDetectionInline]

@admin.register(ConvertedImage)
class ConvertedImageAdmin(admin.ModelAdmin):
  date_hierarchy = 'creationDate'
  list_display = ('id', 'image_id', 'file_name')
  
  def image_id(self,obj):
    return obj.orig.id
  def file_name(self,obj):
    try:
      return obj.file.name
    except ValueError:
      return "NOT_SET"

@admin.register(Detection)
class DetectionAdmin(admin.ModelAdmin):
  date_hierarchy = 'creationDate'
  list_display = ('id', 'type_value')
  inlines = [ImageDetectionInline]
  
  def type_value(self,obj):
    return str(obj.type)

@admin.register(ImageDetection)
class ImageDetectionAdmin(admin.ModelAdmin):
  date_hierarchy = 'creationDate'
  list_display = ('id', 'image_id', 'detection_id', 'file_name','confidence', 'identifier', 'boundingbox')
  
  def boundingbox(self,obj):
    return '({})'.format(','.join([str(obj.boundingBoxTop), str(obj.boundingBoxLeft), str(obj.boundingBoxWidth), str(obj.boundingBoxHeight)]))
  def detection_id(self,obj):
    return obj.detection.id
  def file_name(self,obj):
    try:
      return obj.file.name
    except ValueError:
      return "NOT_SET"