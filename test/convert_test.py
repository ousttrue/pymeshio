# coding: utf-8
import unittest
import io
import pymeshio.common
import pymeshio.pmd.reader
import pymeshio.pmx.reader
import pymeshio.pmx.writer
import pymeshio.converter


PMD_FILE=pymeshio.common.unicode('resources/初音ミクVer2.pmd')
PMX_FILE=pymeshio.common.unicode('resources/初音ミクVer2.pmx')


class TestConvert(unittest.TestCase):
    
    def test_convert(self):
        # convert
        pmd=pymeshio.pmd.reader.read_from_file(PMD_FILE)
        converted=pymeshio.converter.pmd_to_pmx(pmd)
        # validate
        pmx=pymeshio.pmx.reader.read_from_file(PMX_FILE)
        # check diffference
        pmx.diff(converted)
        #self.assertEqual(pmx, converted)
        pymeshio.pmx.writer.write(io.open("tmp.pmx", "wb"), converted)

