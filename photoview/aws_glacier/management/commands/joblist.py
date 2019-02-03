import dateutil
import json

import boto3

from django.core.management.base import BaseCommand, CommandError

from aws_glacier.models import Job

class Command(BaseCommand):
  help = "List jobs"
  
  def add_arguments(self, parser):
    parser.add_argument('job_id', nargs='?', type=str)
    parser.add_argument('account-id')
    parser.add_argument('vault-name')
  
  def handle(self, *args, **options):
    print("LIST JOBS", options)
    glacier_conn = boto3.client('glacier')
    res = glacier_conn.list_jobs(accountId=options['account-id'], vaultName=options['vault-name'])
    for job in res['JobList']:
      print("{}\n  {} {} {}".format(job['JobId'], job['StatusCode'], job['Action'], dateutil.parser.parse(job['CreationDate'])))
