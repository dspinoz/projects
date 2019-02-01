# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from .models import Inventory
from .models import Archive
from .models import Job
from .models import InventoryRetrieval

admin.site.register(Inventory)
admin.site.register(Archive)
admin.site.register(Job)
admin.site.register(InventoryRetrieval)

