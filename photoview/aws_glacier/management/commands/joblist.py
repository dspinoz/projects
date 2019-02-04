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

    for job in res['JobList']:
      availableJobs.append(job['JobId'])
      
      try:
          myjob = Job.objects.get(jobId = job['JobId'])
          
          myjob.available = True
          myjob.availableDate = datetime.now()
          myjob.accountId = options['account-id']
          myjob.vaultName = options['vault-name']
          myjob.parameters = json.dumps(self.getParameters(job))
          myjob.statusCode = job['StatusCode']
          myjob.action = job['Action']
          myjob.creationDate = dateutil.parser.parse(job['CreationDate'])
          myjob.completed = job['Completed']
          myjob.save()
          
      except ObjectDoesNotExist:
        myjob = Job.objects.create(jobId = job['JobId'], parameters = json.dumps(self.getParameters(job)), statusCode = job['StatusCode'], action = job['Action'], creationDate = dateutil.parser.parse(job['CreationDate']), completed = job['Completed'], accountId = options['account-id'], vaultName = options['vault-name'])

      if job['Completed']:
        myjob.completedDate = datetime.now()
        myjob.save()
    
    for myjob in Job.objects.filter(available=True):
      if myjob.jobId not in availableJobs:
        myjob.available = False
        myjob.save()
