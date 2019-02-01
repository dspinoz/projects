import json
from datetime import datetime

from django.test import TestCase

from .models import Inventory

class InventoryDBTests(TestCase):
  def testIsEmpty(self):
    """ check that the database is empty """
    self.assertIs(Inventory.objects.count(), 0)
  def testCreateObject(self):
    self.assertIs(Inventory.objects.count(), 0)
    Inventory.objects.create()
    self.assertIs(Inventory.objects.count(), 1)
  def testCreateObjectWithOutput(self):
    self.assertIs(Inventory.objects.count(), 0)
    Inventory.objects.create(output=json.dumps({}))
    self.assertIs(Inventory.objects.count(), 1)
  def testCreateObjectWithDate(self):
    self.assertIs(Inventory.objects.count(), 0)
    Inventory.objects.create(date=datetime.now())
    self.assertIs(Inventory.objects.count(), 1)
  def testCreateObjectWithParameters(self):
    self.assertIs(Inventory.objects.count(), 0)
    Inventory.objects.create(date=datetime.now(), output=json.dumps({}))
    self.assertIs(Inventory.objects.count(), 1)


class LoadDataTest(TestCase):
  fixtures = ['test-04-archive-recorded']
  def testData(self):
    self.assertIs(Inventory.objects.count(), 1)
    for i in Inventory.objects.all():
      self.assertNotEqual(i.date, None, "Inventory has date set")
      self.assertNotEqual(i.output, None, "Inventory has output set")