#!/usr/bin/env python
# coding: utf-8
"""
pmx file io library.

pmx file format:
    PMDEditor's Lib/PMX仕様/PMX仕様.txt
"""
__author__="ousttrue"
__license__="zlib"
__versioon__="0.0.1"


import io
import os
import struct


class Model(object):
    """pmx data holder

    version: pmx version
    """
    __slots__=[
            'version', # pmx version
            'name', # model name
            'english_name', # model name in english
            'comment', # model comment
            'english_comment', # model comment in english
            ]
    def __init__(self):
        self.version=0.0


class IO(object):
    """pmx loader

    Attributes:
        name: model name
    """
    def __init__(self):
        self.__io=None
        self.__pos=-1
        self.__end=-1
        self.__model=Model()

    def read(self, path: 'filepath') -> Model:
        size=os.path.getsize(path)
        with open(path, "rb") as f:
            if self.load(path, f, size):
                return self.__model

    def load(self, path: 'filepath', io: io.IOBase, size: int) -> bool: 
        self.__io=io
        self.__end=size
        self.__check_position()

        if not self.__loadHeader():
            return False
        self.__check_position()
        # model info
        self.__model.name = self.__read_text()
        self.__model.english_name = self.__read_text()
        self.__model.comment = self.__read_text()
        self.__model.english_comment = self.__read_text()
        return True

    def __str__(self) -> str:
        return '<PmxIO>'

    def __check_position(self):
        self.__pos=self.__io.tell()

    def __unpack(self, fmt: str, size: int) -> "read value as format":
        return struct.unpack(fmt, self.__io.read(size))[0]

    def __loadHeader(self) -> bool:
        signature=self.__unpack("4s", 4)
        if signature!=b"PMX ":
            print("invalid signature", signature)
            return False
        version=self.__unpack("f", 4)
        if version!=2.0:
            print("unknown version", version)
        self.__model.version=version
        # flags
        flag_bytes=self.__unpack("B", 1)
        if flag_bytes!=8:
            print("invalid flag length", flag_bytes)
            return False
        # text encoding
        text_encoding=self.__unpack("B", 1)
        if text_encoding==0:
            def read_text():
                size=self.__unpack("I", 4)
                return self.__unpack("{0}s".format(size), size).decode("UTF16")
        elif text_encoding==1:
            def read_text():
                size=self.__unpack("I", 4)
                return self.__unpack("{0}s".format(size), size).decode("UTF8")
        else:
            print("unknown text encoding", text_encoding)
            return False
        self.__read_text=read_text
        self.__unpack("B", 1)
        self.__unpack("B", 1)
        self.__unpack("B", 1)
        self.__unpack("B", 1)
        self.__unpack("B", 1)
        self.__unpack("B", 1)
        self.__unpack("B", 1)
        return True

