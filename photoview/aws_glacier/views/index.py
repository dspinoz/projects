# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

import aws_glacier

def index(request):
  context = {
    'title': 'Glacier',
    'jobs': aws_glacier.models.Job.objects.filter(available=True),
    'archives': aws_glacier.models.Archive.objects.filter(deletedDate=None),
    'inventory': aws_glacier.models.Inventory.objects.order_by('-date').first(),
  }
  
  return render(request, 'aws_glacier/index.html', context)