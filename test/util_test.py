# coding: utf-8
import unittest
import io
import pymeshio.util
import pymeshio.common


PMX_FILE=pymeshio.common.unicode('resources/初音ミクVer2.pmx')


class TestUtil(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_read(self):
        model=pymeshio.util.GenericModel.read_from_file(PMX_FILE)
        self.assertEqual(pymeshio.util.GenericModel,  model.__class__)

    def test_write(self):
        # read source file
        pass

