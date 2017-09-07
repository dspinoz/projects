#!/usr/bin/python

import unittest
import inspect

# this is a comment
class TestStringMethods(unittest.TestCase):
    """This is the start of the test for String methods.

    Some additional information...
    """

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        """Test the split method of string with 'hello' and 'world'

        Some additional info about split...
        """
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string

        self.assertTrue('WOOPA'.isupper(),'WOOPA')
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    print inspect.getdoc(TestStringMethods)
    for (name,value) in inspect.getmembers(TestStringMethods):
      if name in TestStringMethods.__dict__ and inspect.ismethod(value):
          print name
          print inspect.getdoc(value)
    print "COMMENTS:"
    print inspect.getcomments(TestStringMethods)
    for (name,value) in inspect.getmembers(TestStringMethods):
      if name in TestStringMethods.__dict__ and inspect.ismethod(value):
          print name
          print inspect.getcomments(value)
    unittest.main()
