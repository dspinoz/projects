import boto3

from log_response import log_response

def detect(fd, detect='faces', rek_conn=boto3.client('rekognition')):
  
  endpoint = 'detect_{}'.format(detect)
  
  if detect == 'faces':
    res = rek_conn.detect_faces(Image={'Bytes': fd.read()})
  elif detect == 'labels':
    res = rek_conn.detect_labels(Image={'Bytes': fd.read()})
  elif detect == 'text':
    res = rek_conn.detect_text(Image={'Bytes': fd.read()})
  elif detect == 'celebrities':
    res = rek_conn.recognize_celebrities(Image={'Bytes': fd.read()})
    endpoint = 'recognize_celebrities'

  log_response(endpoint, res)
  
  return res
