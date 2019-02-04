import sys
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
    parser.add_argument('--request-new', action='store_true', default=False, help="Request a new inventory")
  
  def handle(self, *args, **options):
    glacier_conn = boto3.client('glacier')
    
    if 'request_new' in options and options['request_new']:
      print("REQUESTING NEW INVENTORY")
      parameters = {"Type":"inventory-retrieval"}
      res = glacier_conn.initiate_job(accountId=options['account-id'], vaultName=options['vault-name'], jobParameters=parameters)
      
      meta = res['ResponseMetadata']
      headers = meta['HTTPHeaders']
      AWSGlacierRequestResponse.objects.create(requestId = meta['RequestId'], endpoint = 'initiate_job.inventoryretrieval', retryAttempts = meta['RetryAttempts'], statusCode = meta['HTTPStatusCode'], date = dateutil.parser.parse(headers['date']), responseLength = headers['content-length'], responseContentType = headers['content-type'], responseBody = json.dumps(res), accountId = options['account-id'], vaultName = options['vault-name'])

      inventoryJob = res['jobId']
      print("Job created: {}".format(inventoryJob))
      print("Run joblist to get updates")
      
      sys.exit(0)
    
    inventoryRetrieval = InventoryRetrieval.objects.order_by('-lastModifiedDate').first()
    if inventoryRetrieval is None:
      print("THERE IS NO INVENTORY AVAILABLE")
      if Job.objects.filter(action='InventoryRetrieval', completed=False).order_by('-lastModifiedDate').count():
        print("There are inventory jobs pending")
      sys.exit(1)
    
    pendingJobs = Job.objects.filter(action='InventoryRetrieval', completed=False).order_by('-lastModifiedDate')
    print(pendingJobs.count(), "PENDING INVENTORY JOBS")
    for j in pendingJobs:
      print("  {}: {} {}  ".format(j.id, j.jobId, j.lastModifiedDate))
    
    completedJobs = Job.objects.filter(action='InventoryRetrieval', completed=True).order_by('-lastModifiedDate')
    print(completedJobs.count(), "COMPLETED INVENTORY JOBS")
    for j in completedJobs:
      print("  {}: {} {}".format(j.id, j.jobId, j.lastModifiedDate))
      
    inventory = json.loads(inventoryRetrieval.inventory.output)
    print("CURRENT INVENTORY ({})\n({}, {})".format(len(inventory['ArchiveList']), inventoryRetrieval.lastModifiedDate, inventoryRetrieval.job.jobId))
    for a in inventory['ArchiveList']:
      print("  ARCHIVE {}: {} {} {} {}".format(a['ArchiveId'], a['ArchiveDescription'], dateutil.parser.parse(a['CreationDate']), a['Size'], a['SHA256TreeHash']))

