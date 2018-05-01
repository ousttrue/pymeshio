# coding: utf-8
"""
========================
pymeshio
========================

3d mesh io library.
"""
__version__ = '3.1.0'


# export
version = __version__


from . import pmd
from . import pmx
from .converter import pmd_to_pmx


def pmd_from_file(path):
    return pmd.reader.read_from_file(path)


def pmx_from_file(path):
    return pmx.reader.read_from_file(path)
