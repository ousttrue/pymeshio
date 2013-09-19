# coding: utf-8
import sys
import io
import unittest
import pymeshio.common
import pymeshio.obj
import pymeshio.obj.reader
import pymeshio.obj.writer


OBJ_FILE=pymeshio.common.unicode('resources/cube.obj')


class TestObj(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_read(self):
        model=pymeshio.obj.reader.read_from_file(OBJ_FILE)
        self.assertEqual(pymeshio.obj.Model,  model.__class__)
        self.assertEqual(17,  len(model.materials))
        self.assertEqual(140,  len(model.bones))
        self.assertEqual(31,  len(model.morphs))
        self.assertEqual(45,  len(model.rigidbodies))
        self.assertEqual(27,  len(model.joints))

    def test_write(self):
        pass
        """
        # read source file
        buf=pymeshio.common.readall(PMD_FILE)
        # read and write to out
        model=pymeshio.pmd.reader.read(io.BytesIO(buf))
        out=io.BytesIO()
        pymeshio.pmd.writer.write(out, model)
        # read out buffer again
        model2=pymeshio.pmd.reader.read(io.BytesIO(out.getvalue()))
        model.diff(model2)
        self.assertEqual(model, model2)
        """

