import json
from datetime import datetime

from django.test import TestCase

from .models import Inventory



class InventoryDBTests(TestCase):
  def testIsEmpty(self):
    """ check that the database is empty """
    self.assertIs(Inventory.objects.count(), 0)
  def testCreateObject(self):
    Inventory.objects.create()
    self.assertIs(Inventory.objects.count(), 1)
  def testCreateObjectWithOutput(self):
    Inventory.objects.create(output=json.dumps({"ArchiveList":[]}))
    self.assertIs(Inventory.objects.count(), 1)
  def testCreateObjectWithDate(self):
    Inventory.objects.create(date=datetime.now())
    self.assertIs(Inventory.objects.count(), 1)
  def testCreateObjectWithParameters(self):
    Inventory.objects.create(date=datetime.now(), output=json.dumps({"ArchiveList":[]}))
    self.assertIs(Inventory.objects.count(), 1)