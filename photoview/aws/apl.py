#!/usr/bin/env python
import sys
import os
import json
import dateutil.parser
import hashlib
import StringIO
import time

import botocore
import boto3

import db
import util
import treehash

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
showInventory = True
uploadD3JS = False
uploadD3JSTAR = True
uploadABC = True
retrieveArchive = True
showJobs = False

res = glacier_conn.describe_vault(accountId=accountId, vaultName=vaultName)
print("VAULT {} {} {} {} {} {}".format(res['SizeInBytes'], dateutil.parser.parse(res['LastInventoryDate']), res['NumberOfArchives'], dateutil.parser.parse(res['CreationDate']), res['VaultName'], res['VaultARN']))


inventoryJobId = db.has_inventory_job(db_conn)
print("HAS INVENTORY {}".format(inventoryJobId))

if showInventory:
  inventoryJobId = db.get_last_inventory_job(db_conn)
  print("SHOWING INVENTORY",inventoryJobId)
  if inventoryJobId is None:
    print("No inventory available")
  else:
    i = db.get_inventory_output(db_conn, str(inventoryJobId))
    print(i)
    i = json.loads(i)
    print("VAULT",i['VaultARN'],i["InventoryDate"],len(i['ArchiveList']),"ARCHIVES")
    for a in i["ArchiveList"]:
      print("  ",a['ArchiveId'],a['SHA256TreeHash'])
      d = None
      if 'ArchiveDescription' in a:
        d=a['ArchiveDescription']
      print("    ",a['CreationDate'], a['Size'], d)
  sys.exit(1)



def tohex(bstr):
  return ''.join(x.encode('hex') for x in bstr)

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
    filename = "IMG_2390.CR2"
    partSize = 1048576
    a = open(filename,"r")
    
    res = glacier_conn.initiate_multipart_upload(accountId=accountId, vaultName=vaultName, archiveDescription="multipart archive upload 01-miami.mp3", partSize=str(partSize))
    print("NEW MULTIPART UPLOAD",res['location'], res['uploadId'], json.dumps(res))
    
    uploadId = res['uploadId']
    archiveSize = 0
    hasher = hashlib.sha256()
    
    chunks = []
    
    while True:
      b = a.read(partSize)
      print("READ",len(b))
      if not b:
        print("BREAK")
        break
        
      rangeHeader = 'bytes {}-{}/*'.format(archiveSize, archiveSize + len(b) - 1)
      print("RANGE",rangeHeader)
      
      chunk_hasher = hashlib.sha256()
      chunk_hasher.update(b"".join(b))
      
      res = glacier_conn.upload_multipart_part(accountId=accountId, vaultName=vaultName, uploadId=uploadId, range=rangeHeader, body=b''.join(b))
      print("UPLOADED PART", res['checksum'], json.dumps(res))
      print("CHUNK HASH",chunk_hasher.hexdigest(),chunk_hasher.hexdigest() == res['checksum'], res['checksum'])
      chunks.append(chunk_hasher.digest())
      
      archiveSize = archiveSize + len(b)
      hasher.update(b"".join(b))
    
    # only while the upload is valid - before completed
    res = glacier_conn.list_parts(accountId=accountId, vaultName=vaultName, uploadId=uploadId)
    print("PARTS LIST")
    for part in res['Parts']:
      print("PART", json.dumps(part))
    
    
    print("CHECKSUM",archiveSize,"bytes",hasher.hexdigest())
    
    print("CALCULATING TREEHASH FROM",len(chunks),"CHUNKS")
    for c in chunks:
      print("CHUNK",tohex(c))
      
      
      
    while len(chunks) > 1:
      
      new_chunks = []
      
      it = iter(chunks)
      
      while True:
        a = None
        b = None
        try:
          a = next(it)
        except:
          #reached the end of the list
          break
          
        try:
          b = next(it)
        except:
          #only a single element remains - add to new list
          new_chunks.append(a)
          break
          
        pair = (a,b)
      
        h = hashlib.sha256()
        h.update(pair[0])
        h.update(pair[1])
        new_chunks.append(h.digest())
      
      # list of new chunks has been created for processing
      chunks = new_chunks
      
    mytreehash = tohex(chunks[0])
    print("MY TREEHASH", mytreehash)
      
      
    
    h = treehash.SHA256TreeHash(filename)
    treeHash = ''.join(x.encode('hex') for x in h.computeSHA256TreeHash())
    treeHash2 = botocore.utils.calculate_tree_hash(open(filename,"rb"))
    
    print("CHECK TREE HASH",treeHash == mytreehash, mytreehash, treeHash,treeHash == treeHash2,treeHash2)
    
    
    res = glacier_conn.complete_multipart_upload(accountId=accountId, vaultName=vaultName, uploadId=uploadId, archiveSize=str(archiveSize), checksum=mytreehash)
    print("MULTIPART ARCHIVE UPLOADED",res['checksum'] == hasher.hexdigest(), res['checksum'], res['archiveId'], res['location'], json.dumps(res))


if retrieveArchive:
  archiveId = "..."
  
  retrieveParameters = {"Type":"archive-retrieval", "ArchiveId": archiveId, "Tier": "Bulk", "Description": "Retrieve archive"}
  res = glacier_conn.initiate_job(accountId=accountId, vaultName=vaultName, jobParameters=retrieveParameters)
  print("REQUESTING ARCHIVE",archiveId,"WITH JOB",res['jobId'])
  db.add_glacier_job(db_conn, res['jobId'], accountId, vaultName, json.dumps(retrieveParameters), retrieveParameters['Description'], '')
  
  retrieveJob = res['jobId']
  
  while True:
  
    res = glacier_conn.describe_job(accountId=accountId, vaultName=vaultName, jobId=retrieveJob)
    print("DESCRIBE RETRIEVE JOB {} {} {} {}".format(res['Completed'], res['Action'], dateutil.parser.parse(res['CreationDate']), res['StatusCode']))
    
    # in order to confirm the contents with res['ArchiveSHA256TreeHash'] must know the chunks that were uploaded to glacier, or store the hash for the archive when uploading.
    
    if res['Completed']:
      print("** RETRIEVE JOB COMPLETED! **")
      
      res = glacier_conn.get_job_output(accountId=accountId, vaultName=vaultName, jobId=retrieveJob)
      
      body = res['body']
      del res['body']
      print("JOB OUTPUT RESPONSE (no body)", json.dumps(res))
      
      outf = "retrieve"
      fd = open(outf,'w')
      fd.write(body.read())
      fd.close()
      
      print("CREATED FILE",outf,"FROM RETRIEVE JOB")
      print("COMPLETE")
      
      break
    
    n = 30
    sec = 60
    print("Waiting for",n,n*sec)
    for i in range(1,n+1):
      time.sleep(sec)
      print("  been",i,i*sec)
    
    


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

if showJobs or requestNewInventory:
  print("CHECKING ALL JOBS")
  res = glacier_conn.list_jobs(accountId=accountId, vaultName=vaultName)
  for job in res['JobList']:
    print("DESCRIBE JOB {} {} {} {} {}".format(job['JobId'], job['Completed'], job['Action'], dateutil.parser.parse(job['CreationDate']), job['StatusCode']))
    
    if requestNewInventory:
      if job['Completed'] and job['Action'] == 'InventoryRetrieval' and job['JobId'] == inventoryJobId:
        res = glacier_conn.get_job_output(accountId=accountId, vaultName=vaultName, jobId=job['JobId'])
        jobres = res['body'].read()
        
        db.set_inventory_output(db_conn, job['JobId'], jobres)
        print("***** UPDATED INVENTORY OUTPUT ******")
        
        for a in json.loads(jobres)['ArchiveList']:
          print("ARCHIVE {}".format(json.dumps(a)))
          print("ARCHIVE {} {} {} {} {}".format(a['ArchiveId'], a['ArchiveDescription'], dateutil.parser.parse(a['CreationDate']), a['Size'], a['SHA256TreeHash']))


