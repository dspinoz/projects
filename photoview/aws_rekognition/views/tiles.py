# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

import aws_rekognition

def tiles(request):
  context = {
    'title': 'Rekognition',
    #TODO what if the image does not have any thumbnails?
    'tiles': sorted(aws_rekognition.models.ConvertedImage.objects.filter(metadata__iregex=r'"Type": "thumbnail"').filter(metadata__iregex=r'"Width": 128'), key=lambda a: a.getImageCreationDate()),
  }
  
  return render(request, 'aws_rekognition/tiles.html', context)
