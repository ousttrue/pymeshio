# coding: utf-8
"""
========================
pymeshio
========================

3d mesh io library.
"""
__version__='3.1.0'

# export
version=__version__


from . import pmd


def pmd_from_file(path):
    return pmd.reader.read_from_file(path)
