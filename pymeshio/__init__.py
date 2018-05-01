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
from .pmd.reader import read_from_file as pmd_from_file
from . import pmx
from .pmx.reader import read_from_file as pmx_from_file
from .converter import pmd_to_pmx
