#!/usr/bin/env python
import sys
import os
import json
import dateutil.parser
import hashlib
import StringIO

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
requestNewInventory = False
uploadNewArchive = True
uploadD3JS = False
uploadD3JSTAR = True
uploadABC = True


res = glacier_conn.describe_vault(accountId=accountId, vaultName=vaultName)
print("VAULT {} {} {} {} {} {}".format(res['SizeInBytes'], dateutil.parser.parse(res['LastInventoryDate']), res['NumberOfArchives'], dateutil.parser.parse(res['CreationDate']), res['VaultName'], res['VaultARN']))


inventoryJobId = db.has_inventory_job(db_conn)
print("HAS INVENTORY {}".format(inventoryJobId))


class ABCFile():
  
  def __init__(self):
    self.str = list('abcdefg')
    self.got = 0
  
  def read(self,sz):
    
    print("REQUESTING","at",self.got,"want",sz,"left",len(self.str)-self.got,"total",len(self.str))
    
    if self.got == len(self.str):
      print("DONE")
      return None
      
    if self.got+sz > len(self.str):
      sz = len(self.str) - self.got
      print("GET",sz,"REMAIN")
    
    buf = self.str[self.got:self.got+sz]
    print("READ STR","{}:{}".format(self.got,self.got+sz), buf)
    self.got = self.got + sz
    return buf


if uploadNewArchive:
  
  if uploadD3JS:
    res = glacier_conn.upload_archive(accountId=accountId, vaultName=vaultName, archiveDescription="archive description", body=open("d3.js","r"))
    print("Uploading d3.js", res['archiveId'], res['checksum'], res['location'])
  
  if uploadD3JSTAR:
    print("Uploading multipart d3.js.tar")
    d3js = open("d3.tgz", "r")
    buff = None
    hasher = hashlib.sha256()
    while True:
      buff = d3js.read(100000)
      if not buff:
        break
      hasher.update(b''.join(buff))
        
      print(len(buff))
    d3js.close()
    print("HASH",hasher.hexdigest())
    
  if uploadABC:
    a = ABCFile()
    
    res = glacier_conn.initiate_multipart_upload(accountId=accountId, vaultName=vaultName, archiveDescription="multipart archive upload", partSize="2")
    print("NEW MULTIPART UPLOAD",res['location'], res['uploadId'], json.dumps(res))
    
    uploadId = res['uploadId']
    archiveSize = 0
    hasher = hashlib.sha256()
    
    
    while True:
      b = a.read(2)
      print("READ",b)
      if not b:
        print("BREAK")
        break
        
      rangeHeader = 'bytes {}-{}/*'.format(archiveSize, archiveSize + len(b) - 1)
      print("RANGE",rangeHeader)
      res = glacier_conn.upload_multipart_part(accountId=accountId, vaultName=vaultName, uploadId=uploadId, range=rangeHeader, body=b''.join(b))
      print("UPLOADED PART", res['checksum'], json.dumps(res))
      
      archiveSize = archiveSize + len(b)
      hasher.update(b"".join(b))
    
    print("CHECKSUM",archiveSize,"bytes",hasher.hexdigest())
    res = glacier_conn.complete_multipart_upload(accountId=accountId, vaultName=vaultName, uploadId=uploadId, archiveSize=archiveSize, checksum=hasher.hexdigest())
    print("MULTIPART ARCHIVE UPLOADED",res['checksum'] == hasher.hexdigest(), res['checksum'], res['archiveId'], res['location'], json.dumps(res))
    


if requestNewInventory:

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
      print("***** UPDATED INVENTORY OUTPUT ******")
      
      for a in json.loads(jobres)['ArchiveList']:
        print("ARCHIVE {}".format(json.dumps(a)))
        print("ARCHIVE {} {} {} {} {}".format(a['ArchiveId'], a['ArchiveDescription'], dateutil.parser.parse(a['CreationDate']), a['Size'], a['SHA256TreeHash']))


