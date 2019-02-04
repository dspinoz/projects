import sys
import dateutil
from datetime import datetime
import json

import boto3

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from aws_glacier.models import Job
from aws_glacier.models import InventoryRetrieval
from aws_glacier.models import Archive
from aws_glacier.models import AWSGlacierRequestResponse

class Command(BaseCommand):
  help = "Archives"
  
  def add_arguments(self, parser):
    parser.add_argument('account-id')
    parser.add_argument('vault-name')
  
  def handle(self, *args, **options):
    glacier_conn = boto3.client('glacier')
    
    inventoryRetrieval = InventoryRetrieval.objects.filter(inventory__processed=False).order_by('-lastModifiedDate').first()
    if inventoryRetrieval is None:
      print("THERE IS NO INVENTORY AVAILABLE")
      if Job.objects.filter(action='InventoryRetrieval', completed=False).order_by('-lastModifiedDate').count():
        print("There are inventory jobs pending")
      sys.exit(1)
    
    archives = []
    updateCount = 0
    inventory = json.loads(inventoryRetrieval.inventory.output)
    for a in inventory['ArchiveList']:
      updateCount = updateCount + 1
      try:
          archives.append(a['ArchiveId'])
          
          myarchive = Archive.objects.get(archiveId = a['ArchiveId'])
          
          myarchive.accountId = options['account-id']
          myarchive.vaultName = options['vault-name']
          myarchive.creationDate = dateutil.parser.parse(a['CreationDate'])
          myarchive.description = a['ArchiveDescription']
          myarchive.size = a['Size']
          myarchive.sha256TreeHash = a['SHA256TreeHash']
          myarchive.available = True
          myarchive.save()
          
      except ObjectDoesNotExist:
        myarchive = Archive.objects.create(archiveId = a['ArchiveId'], creationDate = dateutil.parser.parse(a['CreationDate']), size = a['Size'], sha256TreeHash = a['SHA256TreeHash'], accountId = options['account-id'], vaultName = options['vault-name'])

      if 'DeletedDate' in a:
        myarchive.deletedDate = dateutil.parser.parse(a['DeletedDate'])
        myarchive.available = False
        myarchive.save()
    
    inventoryRetrieval.inventory.processed = True
    inventoryRetrieval.inventory.save()
    print("Updated {} archives from inventory {} (Job {})".format(updateCount, inventoryRetrieval.inventory.id, inventoryRetrieval.job.jobId))
    
    for a in Archive.objects.filter(available=True):
      if a.archiveId not in archives:
        a.available = False
        a.save()

