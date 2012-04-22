# coding: utf-8
import unittest
import io
import pymeshio.common
import pymeshio.pmd.reader
import pymeshio.pmx.reader
import pymeshio.pmx.writer


PMX_FILE=pymeshio.common.unicode('resources/初音ミクVer2.pmx')
EXPORT_PMX_FILE=pymeshio.common.unicode('resources/untitled.pmx')


class TestExportedPmx(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_exported_diff(self):
        # convert
        pmx=pymeshio.pmx.reader.read_from_file(PMX_FILE)
        exported=pymeshio.pmx.reader.read_from_file(EXPORT_PMX_FILE)

        # validate
        pmx=pymeshio.pmx.reader.read_from_file(PMX_FILE)
        # check diffference
        pmx.diff(exported)
        #self.assertEqual(pmx, exported)
        pymeshio.pmx.writer.write(io.open("tmp.pmx", "wb"), exported)

