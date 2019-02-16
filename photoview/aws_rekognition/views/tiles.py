# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

import aws_rekognition

def tiles(request):
  context = {
    'title': 'Rekognition',
    'tiles': aws_rekognition.models.ConvertedImage.objects.filter(metadata__iregex=r'"Type": "thumbnail"').filter(metadata__iregex=r'"Width": 256').order_by('creationDate'),
  }
  
  return render(request, 'aws_rekognition/tiles.html', context)
