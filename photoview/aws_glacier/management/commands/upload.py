import os
import sys
import dateutil
from datetime import datetime
import json
import hashlib

import boto3

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist

from aws_glacier.models import Job
from aws_glacier.models import AWSGlacierRequestResponse
from aws_glacier.models import Archive, ArchiveUploadRequest, ArchiveUploadPart, UploadPart, ArchiveUpload

class Command(BaseCommand):
  help = "Upload archive"
  
  def add_arguments(self, parser):
    parser.add_argument('--content', nargs='?', type=str)
    parser.add_argument('--description', nargs='?', type=str)
    parser.add_argument('--partsize', nargs='?', type=int, default=1048576)
    parser.add_argument('account-id')
    parser.add_argument('vault-name')
  
  def tohex(self, bstr):
    return ''.join(x.encode('hex') for x in bstr)
  
  def handle(self, *args, **options):
    glacier_conn = boto3.client('glacier')

    if options['content'] is None:
      print("NO ARCHIVE PROVIDED, use --content")
      sys.exit(1)
    if options['description'] is None:
      options['description'] = os.path.basename(options['content'])
    print(options['content'], options['description'])
    if not os.path.isfile(options['content']):
      print("THIS IS NOT A FILE!")
      sys.exit(1)
    
    
    fd = open(options['content'],"r+b")
    
    res = glacier_conn.initiate_multipart_upload(archiveDescription=options['description'], partSize=str(options['partsize']), accountId=options['account-id'], vaultName=options['vault-name'])
    
    meta = res['ResponseMetadata']
    headers = meta['HTTPHeaders']
    resLength = 0
    if 'content-length' in headers:
      resLength = headers['content-length']
    resType = ''
    if 'content-type' in headers:
      resType = headers['content-type']
    AWSGlacierRequestResponse.objects.create(requestId = meta['RequestId'], endpoint = 'initiate_multipart_upload', retryAttempts = meta['RetryAttempts'], statusCode = meta['HTTPStatusCode'], date = dateutil.parser.parse(headers['date']), responseLength = resLength, responseContentType = resType, responseBody = json.dumps(res), accountId = options['account-id'], vaultName = options['vault-name'])
    
    uploadId = res['uploadId']
    print("NEW MULTIPART UPLOAD", uploadId)
    
    uploadRequest = ArchiveUploadRequest.objects.create(uploadId=uploadId, description=options['description'], partSize=str(options['partsize']), filePath=os.path.realpath(options['content']), accountId=options['account-id'], vaultName=options['vault-name'])
    
    
    archiveSize = 0
    archiveHasher = hashlib.sha256()
    
    parts = []
    
    while True:
      b = fd.read(options['partsize'])
      print("READ",len(b))
      if not b:
        print("BREAK, REACHED EOF")
        break
      
      part = ArchiveUploadPart.objects.create(req=uploadRequest, index=len(parts), startByte=archiveSize, endByte=archiveSize + len(b) - 1, accountId=options['account-id'], vaultName=options['vault-name'])
      
      rangeHeader = 'bytes {}-{}/*'.format(part.startByte, part.endByte)
      print("RANGE",rangeHeader)
      
      chunkHasher = hashlib.sha256()
      chunkHasher.update(b"".join(b))
      
      res = glacier_conn.upload_multipart_part(uploadId=uploadId, range=rangeHeader, body=b''.join(b), accountId=options['account-id'], vaultName=options['vault-name'])
      
      meta = res['ResponseMetadata']
      headers = meta['HTTPHeaders']
      resLength = 0
      if 'content-length' in headers:
        resLength = headers['content-length']
      resType = ''
      if 'content-type' in headers:
        resType = headers['content-type']
      AWSGlacierRequestResponse.objects.create(requestId = meta['RequestId'], endpoint = 'upload_multipart_part', retryAttempts = meta['RetryAttempts'], statusCode = meta['HTTPStatusCode'], date = dateutil.parser.parse(headers['date']), responseLength = resLength, responseContentType = resType, responseBody = json.dumps(res), accountId = options['account-id'], vaultName = options['vault-name'])
      
      resChunkCheck = res['checksum']
      print("UPLOADED PART", resChunkCheck)
      print("CHUNK HASH",chunkHasher.hexdigest(),chunkHasher.hexdigest() == resChunkCheck, resChunkCheck)
      parts.append(chunkHasher.digest())
      
      UploadPart.objects.create(upload=uploadRequest, part=part, sha256=chunkHasher.hexdigest())
      
      archiveSize = archiveSize + len(b)
      archiveHasher.update(b"".join(b))
    
    fd.close()
    fd = None
    
    print("COMPLETED UPLOADING FILE IN",len(parts),"PARTS")
    
    # can only be done while the upload is valid - before marked as completed
    res = glacier_conn.list_parts(uploadId=uploadId, accountId=options['account-id'], vaultName=options['vault-name'])
    
    meta = res['ResponseMetadata']
    headers = meta['HTTPHeaders']
    resLength = 0
    if 'content-length' in headers:
      resLength = headers['content-length']
    resType = ''
    if 'content-type' in headers:
      resType = headers['content-type']
    AWSGlacierRequestResponse.objects.create(requestId = meta['RequestId'], endpoint = 'list_parts', retryAttempts = meta['RetryAttempts'], statusCode = meta['HTTPStatusCode'], date = dateutil.parser.parse(headers['date']), responseLength = resLength, responseContentType = resType, responseBody = json.dumps(res), accountId = options['account-id'], vaultName = options['vault-name'])
      
    print("PARTS LIST")
    for part in res['Parts']:
      print("PART", json.dumps(part))
    
    
    print("CHECKSUM",archiveSize,"bytes","HASH", archiveHasher.hexdigest())
    
    uploadRequest.size = archiveSize
    uploadRequest.sha256 = archiveHasher.hexdigest()
    uploadRequest.save()

    print("CALCULATING TREEHASH FROM",len(parts),"PARTS")
    for p in parts:
      print("PART",self.tohex(p))
      
    while len(parts) > 1:
      
      new_parts = []
      
      it = iter(parts)
      
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
          new_parts.append(a)
          break
          
        pair = (a,b)
      
        h = hashlib.sha256()
        h.update(pair[0])
        h.update(pair[1])
        new_parts.append(h.digest())
      
      # list of new chunks has been created for processing
      parts = new_parts
      
    mytreehash = self.tohex(parts[0])
    print("MY TREEHASH", mytreehash)
    
    
    
    res = glacier_conn.complete_multipart_upload(uploadId=uploadId, archiveSize=str(archiveSize), checksum=mytreehash, accountId=options['account-id'], vaultName=options['vault-name'])
    
    meta = res['ResponseMetadata']
    headers = meta['HTTPHeaders']
    resLength = 0
    if 'content-length' in headers:
      resLength = headers['content-length']
    resType = ''
    if 'content-type' in headers:
      resType = headers['content-type']
    AWSGlacierRequestResponse.objects.create(requestId = meta['RequestId'], endpoint = 'complete_multipart_upload', retryAttempts = meta['RetryAttempts'], statusCode = meta['HTTPStatusCode'], date = dateutil.parser.parse(headers['date']), responseLength = resLength, responseContentType = resType, responseBody = json.dumps(res), accountId = options['account-id'], vaultName = options['vault-name'])
    
    newArchiveId = res['archiveId']
    resChecksum = res['checksum']
    
    uploadRequest.sha256TreeHash = mytreehash
    uploadRequest.save()
    
    myarchive = Archive.objects.create(archiveId=newArchiveId, size=archiveSize, sha256=archiveHasher.hexdigest(), sha256TreeHash=mytreehash, description=options['description'], partSize=options['partsize'], available=False, accountId=options['account-id'], vaultName=options['vault-name'])
    
    ArchiveUpload.objects.create(upload=uploadRequest, archive=myarchive)
    
    print("MULTIPART ARCHIVE UPLOADED",resChecksum == mytreehash, resChecksum, newArchiveId)
    if not resChecksum == mytreehash:
      print("INCORRECT TREEHASH FOR UPLOAD!")
    else:
      print("Successfully uploaded {}: {}".format(options['content'], newArchiveId))