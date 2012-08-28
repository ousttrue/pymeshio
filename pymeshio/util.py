# coding: utf-8
import sys
import os


class GenericModel(object):
    def __init__(self):
        super(GenericModel, self).__init__()

    @staticmethod
    def read_from_file(filepath):
        if not os.path.exists(filepath):
            return

        stem, ext=os.path.splitext(filepath)
        ext=ext.lower()

        model=GenericModel()
        if ext==".pmd":
            from .pmd import reader
            m=reader.read_from_file(filepath)

        elif ext==".pmx":
            from .pmx import reader
            m=reader.read_from_file(filepath)

        elif ext==".mqo":
            from .mqo import reader
            m=reader.read_from_file(filepath)

        else:
            print('unknown file type: '+ext)
            return

        return model

