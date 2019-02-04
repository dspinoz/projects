import sys
import dateutil
from datetime import datetime
import json

import boto3

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from aws_glacier.models import Job
from aws_glacier.models import Inventory, InventoryRetrieval
from aws_glacier.models import AWSGlacierRequestResponse

class Command(BaseCommand):
  help = "Job Outputs"
  
  def add_arguments(self, parser):
    parser.add_argument('account-id')
    parser.add_argument('vault-name')
  
  def handle(self, *args, **options):
    glacier_conn = boto3.client('glacier')

    jobs = Job.objects.filter(completed=True, retrievedOutput=False)
    if jobs.count() == 0:
      print("There are no jobs pending outputs. Run joblist to ensure latest information is available")
      sys.exit(0)
    
    print("There are {} jobs with outputs pending".format(jobs.count()))
    
    for job in jobs:
      if job.action == 'InventoryRetrieval':
        res = glacier_conn.get_job_output(accountId=options['account-id'], vaultName=options['vault-name'], jobId=job.jobId)
        
        body = res['body']
        del res['body']
        
        jsonstr = body.read()
        jsonres = json.loads(jsonstr)
    
        meta = res['ResponseMetadata']
        headers = meta['HTTPHeaders']
        AWSGlacierRequestResponse.objects.create(requestId = meta['RequestId'], endpoint = 'get_job_output', retryAttempts = meta['RetryAttempts'], statusCode = meta['HTTPStatusCode'], date = dateutil.parser.parse(headers['date']), responseLength = headers['content-length'], responseContentType = headers['content-type'], responseBody = json.dumps(res), accountId = options['account-id'], vaultName = options['vault-name'])
        
        inventory = Inventory.objects.create(output=jsonstr, date = dateutil.parser.parse(jsonres['InventoryDate']), accountId = options['account-id'], vaultName = options['vault-name'])
        
        retrieval = InventoryRetrieval.objects.create(job=job, inventory=inventory, vault=options['vault-name'])
        
        job.retrievedOutput = True
        job.save()
        
        print("Successfully saved inventory outputs")
      else:
        print("Unsure how to handle {} job".format(job.action))
        sys.exit(1)

