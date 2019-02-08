import dateutil
import json

from aws_rekognition.models import AWSRekognitionRequestResponse

def log_response(endpoint, res):
  meta = res['ResponseMetadata']
  headers = meta['HTTPHeaders']
  AWSRekognitionRequestResponse.objects.create(requestId=meta['RequestId'], endpoint = endpoint, date = dateutil.parser.parse(headers['date']), statusCode = meta['HTTPStatusCode'], retryAttempts = meta['RetryAttempts'], responseLength = headers['content-length'], responseContentType = headers['content-type'], responseBody=json.dumps(res))