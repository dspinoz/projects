import sys
import dateutil
from datetime import datetime
import json

import boto3

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from aws_glacier.models import Job
from aws_glacier.models import AWSGlacierRequestResponse

class Command(BaseCommand):
  help = "Download archive"
  
  def add_arguments(self, parser):
    parser.add_argument('--archive_id', nargs='?', type=str)
    parser.add_argument('account-id')
    parser.add_argument('vault-name')
  
  def handle(self, *args, **options):
    glacier_conn = boto3.client('glacier')

    if options['archive_id'] is None:
      print("NO ARCHIVE PROVIDED, use --archive_id")
      sys.exit(1)

    parameters = {"Type":"archive-retrieval", "ArchiveId": options['archive_id'], "Tier": "Bulk", "Description": "Retrieve archive"}
    res = glacier_conn.initiate_job(accountId=options['account-id'], vaultName=options['vault-name'], jobParameters=parameters)

    meta = res['ResponseMetadata']
    headers = meta['HTTPHeaders']
    AWSGlacierRequestResponse.objects.create(requestId = meta['RequestId'], endpoint = 'initiate_job.archiveretrieval', retryAttempts = meta['RetryAttempts'], statusCode = meta['HTTPStatusCode'], date = dateutil.parser.parse(headers['date']), responseLength = headers['content-length'], responseContentType = headers['content-type'], responseBody = json.dumps(res), accountId = options['account-id'], vaultName = options['vault-name'])
  
    print("REQUESTING ARCHIVE",options['archive_id'],"WITH JOB",res['jobId'])
  