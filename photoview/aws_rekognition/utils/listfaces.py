
import boto3

from log_response import log_response

def list_faces(collectionId, rek_conn=boto3.client('rekognition')):
    res = rek_conn.list_faces(CollectionId=collectionId)
    
    log_response('list_faces', res)
    
    return res
