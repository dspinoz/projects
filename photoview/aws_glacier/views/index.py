# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse

def index(request):
  context = {
    'title': 'Glacier',
  }
  return render(request, 'aws_glacier/index.html', context)