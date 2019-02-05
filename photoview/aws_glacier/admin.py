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
from .models import ArchiveUploadRequest, ArchiveUploadPart, UploadPart, ArchiveUpload

class InventoryRetrievalInline(admin.TabularInline):
  model = InventoryRetrieval

class ArchiveRetrievalInline(admin.TabularInline):
  model = ArchiveRetrieval
  
class UploadPartInline(admin.TabularInline):
  model = UploadPart
  
class ArchiveUploadPartInline(admin.TabularInline):
  model = ArchiveUploadPart

class ArchiveUploadInline(admin.TabularInline):
  model = ArchiveUpload

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
  date_hierarchy = 'creationDate'
  list_display = ('id','jobId', 'action', 'statusCode', 'completed', 'retrievedOutput', 'available')
  list_filter = ('action', 'statusCode', 'completed', 'retrievedOutput', 'creationDate')
  inlines = [InventoryRetrievalInline, ArchiveRetrievalInline]

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
  date_hierarchy = 'date'
  list_display = ('id','date','output')
  list_filter = ('date', )
  inlines = [InventoryRetrievalInline]
  
@admin.register(Archive)
class ArchiveAdmin(admin.ModelAdmin):
  date_hierarchy = 'creationDate'
  list_display = ('id', 'archiveId', 'size', 'sha256TreeHash', 'description', 'creationDate', 'available')
  list_filter = ('creationDate', 'deletedDate')
  inlines = [ArchiveUploadInline, ArchiveRetrievalInline]
  
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
  list_filter = ('date', 'endpoint', 'statusCode', 'responseContentType')

@admin.register(ArchiveUploadRequest)
class ArchiveUploadRequestAdmin(admin.ModelAdmin):
  date_hierarchy='lastModifiedDate'
  list_display = ('id', 'uploadId', 'description', 'filePath', 'size')
  inlines = [UploadPartInline, ArchiveUploadInline]

@admin.register(ArchiveUploadPart)
class ArchiveUploadPartAdmin(admin.ModelAdmin):
  date_hierarchy = 'lastModifiedDate'
  list_display = ('id', 'index', 'startByte', 'endByte')
  inlines = [UploadPartInline]

@admin.register(UploadPart)
class UploadPartAdmin(admin.ModelAdmin):
  date_hierarchy = 'lastModifiedDate'
  list_display = ('id', 'upload_id', 'part_id', 'sha256')
  def upload_id(self,obj):
    return obj.upload.id
  def part_id(self,obj):
    return obj.part.id

@admin.register(ArchiveUpload)
class ArchiveUploadAdmin(admin.ModelAdmin):
  date_hierarchy = 'lastModifiedDate'
  list_display = ('id', 'upload_id', 'archive_id')
  def upload_id(self,obj):
    return obj.upload.id
  def archive_id(self,obj):
    return obj.archive.id