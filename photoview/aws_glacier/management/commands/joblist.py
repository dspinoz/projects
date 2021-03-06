import dateutil
from datetime import datetime
import json

import boto3

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from aws_glacier.models import Job
from aws_glacier.models import AWSGlacierRequestResponse

class Command(BaseCommand):
  help = "List jobs"
  
  def add_arguments(self, parser):
    parser.add_argument('job_id', nargs='?', type=str)
    parser.add_argument('account-id')
    parser.add_argument('vault-name')
  
  def getParameters(self, job):
    if job['Action'] == 'InventoryRetrieval':
      return job['InventoryRetrievalParameters']
    return None
  
  def handle(self, *args, **options):
    glacier_conn = boto3.client('glacier')

    res = glacier_conn.list_jobs(accountId=options['account-id'], vaultName=options['vault-name'])

    meta = res['ResponseMetadata']
    headers = meta['HTTPHeaders']
    AWSGlacierRequestResponse.objects.create(requestId = meta['RequestId'], endpoint = 'list_jobs', retryAttempts = meta['RetryAttempts'], statusCode = meta['HTTPStatusCode'], date = dateutil.parser.parse(headers['date']), responseLength = headers['content-length'], responseContentType = headers['content-type'], responseBody = json.dumps(res), accountId = options['account-id'], vaultName = options['vault-name'])

    availableJobs = []
    completedJobs = False

    for job in res['JobList']:
      availableJobs.append(job['JobId'])
      
      (myjob, newjob) = Job.objects.get_or_create(jobId = job['JobId'])
      
      myjob.available = True
      myjob.availableDate = datetime.now()
      myjob.accountId = options['account-id']
      myjob.vaultName = options['vault-name']
      if job['Action'] == 'InventoryRetrieval':
        myjob.parameters = json.dumps(job['InventoryRetrievalParameters'])
      if job['Action'] == 'ArchiveRetrieval':
        myjob.parameters = json.dumps({"RetrievalByteRange": job["RetrievalByteRange"], "Tier": job["Tier"], "SHA256TreeHash": job["SHA256TreeHash"], "ArchiveId": job["ArchiveId"], "ArchiveSizeInBytes": job["ArchiveSizeInBytes"], "ArchiveSHA256TreeHash": job["ArchiveSHA256TreeHash"]})
      myjob.statusCode = job['StatusCode']
      if 'StatusMessage' in job:
        myjob.statusMessage = job['StatusMessage']
      myjob.action = job['Action']
      if 'JobDescription' in job:
        myjob.description = job['JobDescription']
      myjob.creationDate = dateutil.parser.parse(job['CreationDate'])
      myjob.completed = job['Completed']
      if 'CompletionDate' in job:
        myjob.completedDate = dateutil.parser.parse(job['CompletionDate'])
        if not myjob.retrievedOutput:
          print("JOB {} has recently completed: {}".format(myjob.id, myjob.jobId))
          completedJobs = True
      
      myjob.save()
    
    if completedJobs:
      print("Run joboutputs to get job outputs")
    
    for myjob in Job.objects.filter(available=True):
      if myjob.jobId not in availableJobs:
        myjob.available = False
        myjob.save()
