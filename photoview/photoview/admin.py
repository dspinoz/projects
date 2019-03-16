# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.contrib import admin
from django.utils.html import format_html

# Register your models here.

from .models import ConvertedImage
from .models import IndexedImage
from .models import DelayedCompute

class ConvertedImageInline(admin.TabularInline):
  model = ConvertedImage

class DelayedComputeInline(admin.TabularInline):
  model = DelayedCompute

@admin.register(IndexedImage)
class IndexedImageAdmin(admin.ModelAdmin):
  date_hierarchy = 'creationDate'
  list_display = ('id','filePath', 'width', 'height', 'contentType', 'size')
  list_filter = ('contentType', 'width', 'height')
  inlines = [ConvertedImageInline, DelayedComputeInline]

@admin.register(ConvertedImage)
class ConvertedImageAdmin(admin.ModelAdmin):
  date_hierarchy = 'creationDate'
  list_display = ('id', 'image_id', 'file_name', 'size', 'Type', 'Width', 'file_link')
  
  def image_id(self,obj):
    return obj.orig.id
  def file_name(self,obj):
    try:
      return obj.file.url
    except ValueError:
      return "NOT_SET"
  def file_link(self,obj):
    try:
      return format_html(u'<a href="{}">view</a>', obj.file.url)
    except ValueError:
      return "NOT_SET"
  def Type(self,obj):
    return json.loads(obj.metadata)['Type']
  def Width(self,obj):
    return json.loads(obj.metadata)['Width']

@admin.register(DelayedCompute)
class DelayedComputeAdmin(admin.ModelAdmin):
  date_hierarchy = 'creationDate'
  list_display = ('id', 'image', 'type_value', 'metadata', 'completionDate', 'duration')
  
  def type_value(self,obj):
    return str(obj.type)
  def duration(self,obj):
    if obj.completionDate is None:
      return '-'
    return (obj.completionDate - obj.creationDate).total_seconds()
