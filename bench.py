import os
import sys
import io
from benchmarker import Benchmarker
import pymeshio.common
import pymeshio.pmd.reader
import pymeshio.pmd.reader_konbu

sys.path.append('test')
from fixture import *
PMD_FILE=PYMESHIO_TEST_RESOURCES+'/初音ミクVer2.pmd'
PMD_BYTES=pymeshio.common.readall(PMD_FILE)

## specify number of loop
with Benchmarker(3, width=30) as bench:

    '''
    @bench("io")
    def _(bm):
        for i in bm:
            rawbytes=pymeshio.common.readall(PMD_FILE)

    @bench("reader.read_from_file")
    def _(bm):
        for i in bm:
            m=pymeshio.pmd.reader.read_from_file(PMD_FILE)
    '''

    @bench("reader.read")
    def _(bm):
        for i in bm:
            m=pymeshio.pmd.reader.read(io.BytesIO(PMD_BYTES))

    @bench("reader_konbu.read_from_bytes")
    def _(bm):
        for i in bm:
            m=pymeshio.pmd.reader_konbu.read_from_bytes(PMD_BYTES)

