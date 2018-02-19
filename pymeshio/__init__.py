# coding: utf-8
"""
========================
pymeshio
========================

3d mesh io library.
"""

import pathlib
from typing import Any

from . import mqo
from . import obj
from . import x
from . import pmd
from . import vmd
from . import vpd
from . import pmm
from . import pmx
from . import gltf
from .common import *
from .converter import *

__version__ = '3.1.0'


def read_from_file(src: str)->Any:
    path = pathlib.Path(src)
    ext = path.suffix.lower()
    if ext == '.pmx':
        with path.open('rb') as io:
            return pmx.reader.read(io)
    elif ext == '.pmd':
        with path.open('rb') as io:
            return pmd.reader.read(io)
    else:
        raise Exception('unknown file type: ' + src)
