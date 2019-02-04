import dateutil
from datetime import datetime
import json

import boto3

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from aws_glacier.models import Job
from aws_glacier.models import InventoryRetrieval
from aws_glacier.models import AWSGlacierRequestResponse

class Command(BaseCommand):
  help = "Inventory"
  
  def add_arguments(self, parser):
    parser.add_argument('account-id')
    parser.add_argument('vault-name')
  
  def handle(self, *args, **options):
    glacier_conn = boto3.client('glacier')
    print("INVENTORY LIST")

    inventoryRetrieval = InventoryRetrieval.objects.order_by('lastModifiedDate').first()
    if inventoryRetrieval is None:
      print("THERE IS NO CURRENT INVENTORY")
    else:
      print("INVENTORY", inventoryRetrieval.lastModifiedDate," (", inventoryRetrieval.job.jobId,")")
      inventory = json.loads(inventoryRetrieval.inventory.output)
      print("{} archives".format(len(inventory['ArchiveList'])))
      for a in inventory['ArchiveList']:
        print("ARCHIVE {} {} {} {} {}".format(a['ArchiveId'], a['ArchiveDescription'], dateutil.parser.parse(a['CreationDate']), a['Size'], a['SHA256TreeHash']))

    completedJobs = Job.objects.filter(action='InventoryRetrieval', completed=True).order_by('lastModifiedDate')
    print(completedJobs.count(), "COMPLETED INVENTORY JOBS")
    for j in completedJobs:
      print("  ", j.jobId, j.lastModifiedDate)

    pendingJobs = Job.objects.filter(action='InventoryRetrieval', completed=False).order_by('lastModifiedDate')
    print(pendingJobs.count(), "PENDING INVENTORY JOBS")
    for j in pendingJobs:
      print("  ", j.jobId, j.lastModifiedDate)