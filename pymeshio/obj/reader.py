# coding: utf-8
"""
obj reader
"""
import io
from .. import obj
from .. import common


class Reader(common.TextReader):
    """mqo reader
    """
    __slots__=[
            "has_mikoto",
            "materials", "objects",
            ]
    def __init__(self, ios):
        super(Reader, self).__init__(ios)

    def __str__(self):
        return "<MQO %d lines, %d materials, %d objects>" % (
                self.lines, len(self.materials), len(self.objects))

    def read(self):
        pass


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
    return Reader(ios).read()

