# coding: utf-8
import unittest
import io
import pymeshio.util
import pymeshio.common
import pymeshio.pmx.reader


PMX_FILE=pymeshio.common.unicode('resources/初音ミクVer2.pmx')


class TestUtil(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_read(self):
        src=pymeshio.pmx.reader.read_from_file(PMX_FILE)
        model=pymeshio.util.GenericModel.read_from_file(PMX_FILE)
        self.assertEqual(pymeshio.util.GenericModel,  model.__class__)
        self.assertEqual(len(src.vertices), len(model.meshes[0].vertices))
        self.assertEqual(len(src.textures), len(model.textures))
        self.assertEqual(len(src.materials), len(model.materials))
        self.assertEqual(len(src.indices)/3, len(model.meshes[0].faces))

    def test_write(self):
        # read source file
        pass

