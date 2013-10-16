import pymeshio.x
import pymeshio.x.reader
import sys
import unittest


FILE="resources/cube.x"


class TestX(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_read(self):
        model=pymeshio.x.reader.read_from_file(FILE)
        #print(model)
        self.assertEqual(pymeshio.x.Model, model.__class__)
        self.assertEqual(20, len(model.vertices))
        self.assertEqual(1, len(model.materials))

