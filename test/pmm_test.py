# coding: utf-8
import sys
import io
import unittest
import pymeshio.common
import pymeshio.pmm
import pymeshio.pmm.reader
#import pymeshio.pmm.writer


PMM_FILE=pymeshio.common.unicode('resources/UserFile/サンプル（きしめん).pmm')


class TestPmm(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_read(self):
        project=pymeshio.pmm.reader.read_from_file(PMM_FILE)
        print(project)

