#!/usr/bin/env python
# coding: utf-8
"""
pmx file io library.

pmx file format:
    PMDEditor's Lib/PMX仕様/PMX仕様.txt
"""
__author__="ousttrue"
__license__="zlib"
__versioon__="1.0.0"


import io
import os
import struct
from . import common


class ParseException(Exception):
    pass


class Deform(object):
    pass


class Bdef1(object):
    """bone deform. use a weight

    Attributes: see __init__
    """
    __slots__=[ 'bone_index']
    def __init__(self, bone_index: int):
        self.bone_index=bone_index


class Bdef2(object):
    """bone deform. use two weights

    Attributes: see __init__
    """
    __slots__=[ 'index0', 'index1', 'weight0']
    def __init__(self, 
            index0: int,
            index1: int,
            weight0: float):
        self.index0=index0
        self.index1=index1
        self.weight0=weight0


class Vertex(object):
    """pmx vertex

    Attributes: see __init__
    """
    __slots__=[ 'position', 'normal', 'uv', 'deform', 'edge_factor' ]
    def __init__(self, 
            position: common.Vector3, 
            normal: common.Vector3, 
            uv: common.Vector2, 
            deform: Deform, 
            edge_factor: float):
        self.position=position 
        self.normal=normal
        self.uv=uv
        self.deform=deform
        self.edge_factor=edge_factor


class Model(object):
    """pmx data representation

    Attributes:
        version: pmx version(expected 2.0)
        name: 
        english_name: 
        comment: 
        english_comment: 
        vertices:
    """
    __slots__=[
            'version', # pmx version
            'name', # model name
            'english_name', # model name in english
            'comment', # model comment
            'english_comment', # model comment in english
            'vertices'
            ]
    def __init__(self):
        self.version=0.0
        self.name=''
        self.english_name=''
        self.comment=''
        self.english_comment=''
        self.vertices=[]


class IO(object):
    """pmx loader

    Attributes:
        text_encoding: 
        extended_uv:
        vertex_index_size:
        texture_index_size:
        material_index_size:
        bone_index_size:
        morph_index_size:
        rigidbody_index_size:
    """
    def __init__(self):
        self.__io=None
        self.__pos=-1
        self.__end=-1
        self.__model=Model()

    def read(self, path: 'filepath') -> Model:
        size=os.path.getsize(path)
        with open(path, "rb") as f:
            if self.__load(path, f, size):
                return self.__model

    def __load(self, path: 'filepath', io: io.IOBase, size: int) -> bool: 
        self.__io=io
        self.__end=size
        self.__pos=0

        ####################
        # header
        ####################
        signature=self.__unpack("4s", 4)
        if signature!=b"PMX ":
            print("invalid signature", self.signature)
            return False
        version=self.__unpack("f", 4)
        if version!=2.0:
            print("unknown version", version)
        self.__model.version=version
        # flags
        flag_bytes=self.__unpack("B", 1)
        if flag_bytes!=8:
            print("invalid flag length", self.flag_bytes)
            return False
        # text encoding
        self.text_encoding=self.__unpack("B", 1)
        self.__read_text=self.__get_read_text()
        # uv
        self.extended_uv=self.__unpack("B", 1)
        if self.extended_uv>0:
            print("extended uv is not supported", self.extended_uv)
            return False
        # index size
        self.vertex_index_size=self.__unpack("B", 1)
        self.texture_index_size=self.__unpack("B", 1)
        self.material_index_size=self.__unpack("B", 1)
        self.bone_index_size=self.__unpack("B", 1)
        self.morph_index_size=self.__unpack("B", 1)
        self.rigidbody_index_size=self.__unpack("B", 1)

        ####################
        # model info
        ####################
        self.__model.name = self.__read_text()
        self.__model.english_name = self.__read_text()
        self.__model.comment = self.__read_text()
        self.__model.english_comment = self.__read_text()

        ####################
        # vertices
        ####################
        #vertex_count=self.__read_int(self.vertex_index_size)
        # pmdeditor 131c bug?
        vertex_count=self.__read_int(4)
        self.__model.vertices=[self.__read_vertex() for i in range(vertex_count)]

        return True

    def __str__(self) -> str:
        return '<PmxIO>'

    def __check_position(self):
        self.__pos=self.__io.tell()

    def __unpack(self, fmt: str, size: int) -> "read value as format":
        result=struct.unpack(fmt, self.__io.read(size))
        self.__check_position()
        return result[0]

    def __get_read_text(self) -> "text process function":
        if self.text_encoding==0:
            def read_text():
                size=self.__unpack("I", 4)
                return self.__unpack("{0}s".format(size), size).decode("UTF16")
            return read_text
        elif self.text_encoding==1:
            def read_text():
                size=self.__unpack("I", 4)
                return self.__unpack("{0}s".format(size), size).decode("UTF8")
            return read_text
        else:
            print("unknown text encoding", self.text_encoding)

    def __read_int(self, size):
        if size==1:
            return self.__unpack("B", size)
        if size==2:
            return self.__unpack("H", size)
        if size==4:
            return self.__unpack("I", size)
        print("not reach here")
        raise ParseException("invalid int size: "+size)

    def __read_vertex(self):
        return Vertex(
                self.__read_vector3(), # pos
                self.__read_vector3(), # normal
                self.__read_vector2(), # uv
                self.__read_deform(), # deform(bone weight)
                self.__unpack("f", 4) # edge factor
                )

    def __read_vector2(self):
        print(self.__pos)
        return common.Vector2(
                self.__unpack("f", 4), 
                self.__unpack("f", 4)
                )

    def __read_vector3(self):
        print(self.__pos)
        return common.Vector3(
                self.__unpack("f", 4), 
                self.__unpack("f", 4), 
                self.__unpack("f", 4)
                )

    def __read_deform(self):
        print(self.__pos)
        deform_type=self.__unpack("B", 1)
        if deform_type==0:
            return Bdef1(self.__read_int(self.bone_index_size))
        if deform_type==1:
            return Bdef2(
                    self.__read_int(self.bone_index_size),
                    self.__read_int(self.bone_index_size),
                    self.__unpack("f", 4)
                    )
        """
        if deform_type==2:
            return Bdef4(
                    self.__read_int(self.bone_index_size),
                    self.__read_int(self.bone_index_size),
                    self.__read_int(self.bone_index_size),
                    self.__read_int(self.bone_index_size),
                    self.__unpack("f", 4), self.__unpack("f", 4),
                    self.__unpack("f", 4), self.__unpack("f", 4)
                    )
        """
        raise ParseException("unknown deform type: {0}".format(deform_type))

