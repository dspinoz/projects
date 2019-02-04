import sys
import dateutil
from datetime import datetime
import json

import boto3

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from aws_glacier.models import Job
from aws_glacier.models import Archive, ArchiveRetrieval
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
    
    supportedJobs = ['InventoryRetrieval', 'ArchiveRetrieval']
    
    for job in jobs:
      if job.action not in supportedJobs:
        print("Unsure how to handle {} job".format(job.action))
        sys.exit(1)
      
      res = glacier_conn.get_job_output(accountId=options['account-id'], vaultName=options['vault-name'], jobId=job.jobId)
        
      body = res['body']
      del res['body']
        
      meta = res['ResponseMetadata']
      headers = meta['HTTPHeaders']
      AWSGlacierRequestResponse.objects.create(requestId = meta['RequestId'], endpoint = 'get_job_output.{}'.format(job.action.lower()), retryAttempts = meta['RetryAttempts'], statusCode = meta['HTTPStatusCode'], date = dateutil.parser.parse(headers['date']), responseLength = headers['content-length'], responseContentType = headers['content-type'], responseBody = json.dumps(res), accountId = options['account-id'], vaultName = options['vault-name'])
      
      if job.action == 'InventoryRetrieval':
        jsonstr = body.read()
        jsonres = json.loads(jsonstr)
        
        inventory = Inventory.objects.create(output=jsonstr, date = dateutil.parser.parse(jsonres['InventoryDate']), accountId = options['account-id'], vaultName = options['vault-name'])
        
        retrieval = InventoryRetrieval.objects.create(job=job, inventory=inventory, vault=options['vault-name'])
        
        job.retrievedOutput = True
        job.save()
        
        print("Successfully saved inventory outputs")
        
      elif job.action == 'ArchiveRetrieval':
        
        jobparams = json.loads(job.parameters)
        (myarchive, newarchive) = Archive.objects.get_or_create(archiveId = jobparams['ArchiveId'], size = jobparams['ArchiveSizeInBytes'])
        
        if newarchive:
          myarchive.accountId = options['account-id']
          myarchive.vaultName = options['vault-name']
          myarchive.sha256TreeHash = jobparams['ArchiveSHA256TreeHash']
          myarchive.available = True
          myarchive.save()
        
        range = jobparams['RetrievalByteRange'].split('-')
        retrieval = ArchiveRetrieval.objects.create(job=job, archive=myarchive, startByte=range[0], endByte=range[1])
        
        outf = "retrieve"
        fd = open(outf,'w')
        fd.write(body.read())
        fd.close()
      
        print("CREATED FILE",outf,"FROM RETRIEVE JOB")
        
        job.retrievedOutput = True
        job.save()
        
        print("Successfully completed archive retrieval")
