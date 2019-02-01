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

class InventoryDataTest(TestCase):
  def testInventoryRetrievalJobAndOutput(self):
    # initiating job from AWS ...
    self.assertIs(Job.objects.count(), 0, "No jobs recorded yet")
    Job.objects.create(jobId="aaa")
    self.assertIs(Job.objects.count(), 1, "Job inserted to database")
    j = Job.objects.get(jobId="aaa")
    self.assertNotEqual(j, None, "Job retrieved from database")
    self.assertIs(j.completed, False, "Job is not completed")
    self.assertEqual(j.inventoryretrieval_set.count(), 0, "Job has no inventory retrieval recorded")
    # waiting for job to complete ...
    j.completed = True
    j.save()
    self.assertIs(j.completed, True, "Job is now completed")
    self.assertIs(j.retrievedOutput, False, "Job has not yet retrieved outputs")
    #retrieving outputs from AWS ...
    self.assertIs(Inventory.objects.count(), 0, "No inventories recorded yet")
    i = Inventory.objects.create(output=json.dumps({"ArchiveList":[]}))
    self.assertNotEqual(i.date, None, "Inventory has date set")
    self.assertNotEqual(i.output, None, "Inventory has output set")
    self.assertIs(Inventory.objects.count(), 1, "Inventory has been recorded")
    # link outputs to job and log as inventory retrieval
    j.retrievedOutput = True
    j.save()
    self.assertIs(j.retrievedOutput, True, "Job has outputs retrieved")
    self.assertIs(InventoryRetrieval.objects.count(), 0, "No retrievals recorded yet")
    r = InventoryRetrieval.objects.create(job=j, inventory=i)
    self.assertNotEqual(r.job, None, "Retrieval has job")
    self.assertNotEqual(r.inventory, None, "Retrieval has inventory")
    self.assertIs(InventoryRetrieval.objects.count(), 1, "Retrievals has been recorded")
    # check retrievals are recorded in all objects
    for r in InventoryRetrieval.objects.all():
      self.assertEqual(r.job.jobId, "aaa", "Retrieval has correct job id")
      self.assertIs(r.inventory.id, 1, "Retrieval has inventory recorded")
    for j in Job.objects.all():
       self.assertEqual(j.jobId, "aaa", "Job id is correct")
       self.assertEqual(j.inventoryretrieval_set.count(), 1, "Job has inventory retrievals recorded")
       for r in j.inventoryretrieval_set.all():
         self.assertEqual(r.id, 1, "Job has Retrieval set")
         # as job is an inventory retrieval, get the output
         self.assertNotEqual(r.inventory.output, "", "Inventory for retrieval is set")
         output = json.loads(r.inventory.output)
         self.assertEqual(output['ArchiveList'], [], "Inventory has empty archive list")