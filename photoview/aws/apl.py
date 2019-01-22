#!/usr/bin/env python
import os
import json

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

inventoryJobId = db.has_inventory_job(db_conn)

if inventoryJobId is None:
  print("REQUESTING INVENTORY")
  res = glacier_conn.initiate_job(accountId=accountId, vaultName=vaultName, jobParameters=parameters)
  db.add_glacier_job(db_conn, res['jobId'], accountId, vaultName, json.dumps(parameters), '', '')
  inventoryJobId = db.has_inventory_job(db_conn)
  print("REQUESTING INVENTORY {}".format(inventoryJobId))

res = glacier_conn.describe_job(accountId=accountId, vaultName=vaultName, jobId=inventoryJobId)
print("DESCRIBE JOB {}".format(json.dumps(res)))

if res['Completed']:
  print("Inventory job completed")
  #TODO update database
else:
  print("inventory job is running",res['StatusCode'])
  
res = glacier_conn.list_jobs(accountId=accountId, vaultName=vaultName)
for job in res['JobList']:
  print("JOB {}".format(json.dumps(job)))
  if job['Completed']:
    res = glacier_conn.get_job_output(accountId=accountId, vaultName=vaultName, jobId=inventoryJobId)
    jobres = res['body'].read()
    for a in json.loads(jobres)['ArchiveList']:
      print("ARCHIVE {}".format(json.dumps(a)))


