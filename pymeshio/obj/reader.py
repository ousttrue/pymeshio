# coding: utf-8
"""
obj reader
"""
import io
from .. import obj


def read_from_file(path):
    """
    read from file path, then return the pymeshio.mqo.Model.

    :Parameters:
      path
        file path
    """
    with io.open(path, 'rb') as ios:
        return read(ios)


def read(ios):
    """
    read from ios, then return the pymeshio.mqo.Model.

    :Parameters:
      ios
        input stream (in io.IOBase)
    """
    assert(isinstance(ios, io.IOBase))
    return None

