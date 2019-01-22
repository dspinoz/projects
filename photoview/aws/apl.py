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
  res = glacier_conn.initiate_job(accountId=accountId, vaultName=vaultName, jobParameters=parameters)
  db.add_glacier_job(db_conn, res['jobId'], accountId, vaultName, json.dumps(parameters), '', '')
  inventoryJobId = db.has_inventory_job(db_conn)

res = glacier_conn.describe_job(accountId=accountId, vaultName=vaultName, jobId=inventoryJobId)
print(json.dumps(res))

if res['Completed']:
  print("Inventory job completed")
  #TODO update database
else:
  print("inventory job is running",res['StatusCode'])


