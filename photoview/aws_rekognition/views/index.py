# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

import aws_rekognition

def index(request):
  context = {
    'title': 'Rekognition',
    'images': aws_rekognition.models.IndexedImage.objects.all(),
  }
  
  return render(request, 'aws_rekognition/index.html', context)