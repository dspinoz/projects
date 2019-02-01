import json
from datetime import datetime

from django.test import TestCase

from .models import Inventory
from .models import Job
from .models import InventoryRetrieval

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
  def testInventoryObjects(self):
    self.assertIs(Inventory.objects.count(), 1)
    for i in Inventory.objects.all():
      self.assertNotEqual(i.date, None, "Inventory has date set")
      self.assertNotEqual(i.output, None, "Inventory has output set")
  def testJobObjects(self):
    self.assertIs(Job.objects.count(), 1)
    for j in Job.objects.all():
      self.assertNotEqual(j.jobId, None, "Job has id set")
      self.assertNotEqual(j.creationDate, None, "Job has creation date set")
      self.assertEqual(j.completed, True, "Job is completed")
      self.assertNotEqual(j.description, None, "Job has description set")
  def testInventoryRetrievalObject(self):
    self.assertIs(InventoryRetrieval.objects.count(), 1)
    for r in InventoryRetrieval.objects.all():
      self.assertNotEqual(r.job, None, "Inventory retrieval has job set")
      self.assertNotEqual(r.inventory, None, "Inventory retrieval has inventory set")
    