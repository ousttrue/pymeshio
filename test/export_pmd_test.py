# coding: utf-8
import unittest
import io
import pymeshio.common
import pymeshio.pmd.reader
import pymeshio.pmx.reader
import pymeshio.pmx.writer


PMD_FILE=pymeshio.common.unicode('resources/初音ミクVer2.pmd')
EXPORT_PMD_FILE=pymeshio.common.unicode('resources/untitled.pmd')


class TestExportedPmx(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_exported_diff(self):
        # convert
        pmd=pymeshio.pmd.reader.read_from_file(PMX_FILE)
        exported=pymeshio.pmd.reader.read_from_file(EXPORT_PMX_FILE)

        # validate
        pmx=pymeshio.pmd.reader.read_from_file(PMX_FILE)
        # check diffference
        pmd.diff(exported)
        #self.assertEqual(pmd, exported)
        pymeshio.pmd.writer.write(io.open("tmp.pmd", "wb"), exported)

