import json

from django.core.management.base import BaseCommand

import aws_rekognition.utils as u

class Command(BaseCommand):
  help = "List Faces"
  
  def add_arguments(self, parser):
    parser.add_argument('collection-id')
  
  def handle(self, *args, **options):
    print(json.dumps(u.list_faces(options['collection-id'])))