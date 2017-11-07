# coding: utf-8
import unittest
import os
import io
import pymeshio.common
import pymeshio.pmd.reader
import pymeshio.pmx.reader
import pymeshio.pmx.writer
import pymeshio.converter
from .fixture import PYMESHIO_TEST_RESOURCES

PMD_FILE = pymeshio.common.unicode(PYMESHIO_TEST_RESOURCES + '/初音ミクVer2.pmd')
PMX_FILE = pymeshio.common.unicode(PYMESHIO_TEST_RESOURCES + '/初音ミクVer2.pmx')


class TestConvert(unittest.TestCase):

    def test_convert(self):
        # convert
        pmd = pymeshio.pmd.reader.read_from_file(PMD_FILE)
        converted = pymeshio.converter.pmd_to_pmx(pmd)
        # validate
        if os.path.exists(PMX_FILE):
            pmx = pymeshio.pmx.reader.read_from_file(PMX_FILE)
            # check diffference
            pmx.diff(converted)
            #self.assertEqual(pmx, converted)
            with io.open(PYMESHIO_TEST_RESOURCES + "/tmp.pmx", "wb") as f:
                pymeshio.pmx.writer.write(f, converted)
        else:
            with io.open(PMX_FILE, "wb") as f:
                pymeshio.pmx.writer.write(f, converted)
