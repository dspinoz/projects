# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from .models import Inventory
from .models import Archive
from .models import Job
from .models import ArchiveRetrieval
from .models import InventoryRetrieval
from .models import AWSGlacierRequestResponse

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
  date_hierarchy = 'creationDate'
  list_display = ('id','jobId', 'action', 'statusCode', 'completed', 'retrievedOutput', 'available')
  list_filter = ('action', 'statusCode', 'completed', 'retrievedOutput', 'creationDate')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
  date_hierarchy = 'date'
  list_display = ('id','date','output')
  list_filter = ('date', )
  
@admin.register(Archive)
class ArchiveAdmin(admin.ModelAdmin):
  date_hierarchy = 'creationDate'
  list_display = ('id', 'archiveId', 'size', 'sha256TreeHash', 'description', 'creationDate', 'available')
  list_filter = ('creationDate', 'deletedDate')
  
  def available(self,obj):
    return obj.deletedDate is None

@admin.register(InventoryRetrieval)
class InventoryRetrievalAdmin(admin.ModelAdmin):
  date_hierarchy = 'lastModifiedDate'
  list_display = ('id', 'job_id', 'inventory_id', 'lastModifiedDate')
  list_filter = ('lastModifiedDate', )
  
  def job_id(self, obj):
    return obj.job.id
  def inventory_id(self, obj):
    return obj.inventory.id

@admin.register(ArchiveRetrieval)
class ArchiveRetrievalAdmin(admin.ModelAdmin):
  date_hierarchy = 'lastModifiedDate'
  list_display = ('id', 'job_id', 'archive_id', 'lastModifiedDate', 'startByte', 'endByte', 'content_file_name', 'content_size')
  list_filter = ('lastModifiedDate', )
  
  def job_id(self, obj):
    return obj.job.id
  def archive_id(self, obj):
    return obj.archive.id
  def content_file_name(self,obj):
    try:
      return obj.content.file.name
    except ValueError:
      return "NOT_SET"
  def content_size(self,obj):
    try:
      return obj.content.size
    except ValueError:
      return "NOT_SET"
  
@admin.register(AWSGlacierRequestResponse)
class AWSGlacierRequestResponseAdmin(admin.ModelAdmin):
  date_hierarchy = 'date'
  list_display = ('id', 'requestId', 'endpoint', 'statusCode', 'retryAttempts', 'responseContentType', 'responseLength')
