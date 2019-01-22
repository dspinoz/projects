#!/usr/bin/env python
import sys
import os
import json
import dateutil.parser

import boto3

import db
import util

print("AWS Photo Library")

if util.data_dir(err=False) is None:
  data_dir = os.path.join(os.getcwd(),util.dir_name)
  os.makedirs(data_dir)

db_conn = util.init()
glacier_conn = boto3.client('glacier')

accountId = '-'
vaultName = 'test'
parameters = {"Type":"inventory-retrieval"}


res = glacier_conn.describe_vault(accountId=accountId, vaultName=vaultName)
print("VAULT {} {} {} {} {} {}".format(res['SizeInBytes'], dateutil.parser.parse(res['LastInventoryDate']), res['NumberOfArchives'], dateutil.parser.parse(res['CreationDate']), res['VaultName'], res['VaultARN']))


inventoryJobId = db.has_inventory_job(db_conn)
print("HAS INVENTORY {}".format(inventoryJobId))

if inventoryJobId is None:
  print("REQUESTING INVENTORY")
  res = glacier_conn.initiate_job(accountId=accountId, vaultName=vaultName, jobParameters=parameters)
  db.add_glacier_job(db_conn, res['jobId'], accountId, vaultName, json.dumps(parameters), '', '')
  inventoryJobId = db.has_inventory_job(db_conn)
  print("REQUESTING INVENTORY {}".format(inventoryJobId))

res = glacier_conn.describe_job(accountId=accountId, vaultName=vaultName, jobId=inventoryJobId)
print("DESCRIBE INVENTORY JOB {} {} {} {}".format(res['Completed'], res['Action'], dateutil.parser.parse(res['CreationDate']), res['StatusCode']))

if res['Completed']:
  print("Inventory job completed")
  #TODO update database
else:
  print("inventory job is running",res['StatusCode'])
  
print("CHECKING ALL JOBS")
res = glacier_conn.list_jobs(accountId=accountId, vaultName=vaultName)
for job in res['JobList']:
  print("DESCRIBE JOB {} {} {} {} {}".format(job['JobId'], job['Completed'], job['Action'], dateutil.parser.parse(job['CreationDate']), job['StatusCode']))
  if job['Completed'] and job['Action'] == 'InventoryRetrieval':
    res = glacier_conn.get_job_output(accountId=accountId, vaultName=vaultName, jobId=job['JobId'])
    jobres = res['body'].read()
    
    db.set_inventory_output(db_conn, inventoryJobId, jobres)
    print("UPDATED INVENTORY OUTPUT")
    
    for a in json.loads(jobres)['ArchiveList']:
      print("ARCHIVE {}".format(a['ArchiveId'], a['ArchiveDescription'], dateutil.parser.parse(a['CreationDate']), a['Size'], a['SHA256TreeHash']))


