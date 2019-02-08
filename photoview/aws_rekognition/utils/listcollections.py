import boto3

from log_response import log_response

def list_collections(rek_conn=boto3.client('rekognition')):
    
    res = rek_conn.list_collections()
    
    log_response('list_collections', res)
    
    return res
