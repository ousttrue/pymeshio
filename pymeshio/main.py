# coding: utf-8
"""
"""


import sys
import os
import io
from .pmd import reader
from .pmx import writer
from . import converter


def pmd_to_pmx():
    if len(sys.argv)<3:
        print("usage: %s {input pmd_file} {out pmx_file}" % os.path.basename(sys.argv[0]))
        sys.exit()
    pmd=reader.read_from_file(sys.argv[1])
    pmx=converter.pmd_to_pmx(pmd)
    writer.write(io.open(sys.argv[2], "wb"), pmx)

