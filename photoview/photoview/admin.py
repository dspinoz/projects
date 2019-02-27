# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from .models import ConvertedImage
from .models import IndexedImage

class ConvertedImageInline(admin.TabularInline):
  model = ConvertedImage

@admin.register(IndexedImage)
class IndexedImageAdmin(admin.ModelAdmin):
  date_hierarchy = 'creationDate'
  list_display = ('id','filePath', 'width', 'height', 'contentType', 'size')
  list_filter = ('contentType', 'width', 'height')
  inlines = [ConvertedImageInline]

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
