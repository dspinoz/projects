import json

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

import aws_rekognition.utils as u

class Command(BaseCommand):
  help = "List Collections"
  
  def handle(self, *args, **options):
    print(json.dumps(u.list_collections()))