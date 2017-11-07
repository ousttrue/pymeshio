import os
import unittest
import pymeshio.x
import pymeshio.x.reader


FILE = "resources/cube.x"


class TestX(unittest.TestCase):

    def setUp(self):
        pass

    def test_read(self):
        if not os.path.exists(FILE):
            return
        model = pymeshio.x.reader.read_from_file(FILE)
        # print(model)
        self.assertEqual(pymeshio.x.Model, model.__class__)
        self.assertEqual(24, len(model.vertices))
        self.assertEqual(1, len(model.materials))
