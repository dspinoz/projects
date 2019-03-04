# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

import photoview
import aws_rekognition

def see(request, picid, size=512):
  picid = int(picid)
  context = {
    'title': 'Rekognition',
    'mainpic': photoview.models.IndexedImage.objects.get(id=picid),
    'mainpic_view': photoview.models.IndexedImage.objects.get(id=picid).getConversion(size),
    'tiles': [],
  }
  
  context['tiles'] = sorted(aws_rekognition.models.ConvertedImage.objects.filter(metadata__iregex=r'"Type": "thumbnail"').filter(metadata__iregex=r'"Width": 128'), key=lambda a: a.getImageCreationDate())
  
  for i in range(0,len(context['tiles'])):
    if context['tiles'][i].orig.id == picid:
      before = context['tiles'][i-5:i-1]
      after = context['tiles'][i:i+5]
      context['tiles'] = before + context['tiles'][i:i] + after
      break
  
  return render(request, 'aws_rekognition/see.html', context)
