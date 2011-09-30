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


class Material(object):
    """material

    Attributes: see __init__
    """
    __slots__=[
            'name',
            'english_name',
            'diffuse_color',
            'diffuse_alpha',
            'specular_color',
            'specular_factor',
            'ambient_color',
            'flag',
            'edge_color',
            'edge_size',
            'texture_index',
            'sphia_texture_index',
            'sphia_mode',
            'toon_sharing_flag',
            'toon_texture_index',
            'comment',
            'index_count',
            ]
    def __init__(self,
            name: str,
            english_name: str,
            diffuse_color: common.RGB,
            diffuse_alpha: float,
            specular_color: common.RGB,
            specular_factor: float,
            ambient_color: common.RGB,
            flag: int,
            edge_color: common.RGBA,
            edge_size: float,
            texture_index: int,
            sphia_texture_index: int,
            sphia_mode: int,
            toon_sharing_flag: int
            ):
        self.name=name
        self.english_name=english_name
        self.diffuse_color=diffuse_color
        self.diffuse_alpha=diffuse_alpha
        self.specular_color=specular_color
        self.specular_factor=specular_factor
        self.ambient_color=ambient_color
        self.flag=flag
        self.edge_color=edge_color
        self.edge_size=edge_size
        self.texture_index=texture_index
        self.sphia_texture_index=sphia_texture_index
        self.sphia_mode=sphia_mode
        self.toon_sharing_flag=toon_sharing_flag
        #
        self.toon_texture_index=None
        self.comment=''
        self.index_count=0


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
        textures:
        materials:
        bones:
    """
    __slots__=[
            'version', # pmx version
            'name', # model name
            'english_name', # model name in english
            'comment', # model comment
            'english_comment', # model comment in english
            'vertices',
            'indices',
            'textures',
            'materials',
            'bones',
            ]
    def __init__(self):
        self.version=0.0
        self.name=''
        self.english_name=''
        self.comment=''
        self.english_comment=''
        self.vertices=[]
        self.indices=[]
        self.textures=[]
        self.materials=[]
        self.bones=[]


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
        vertex_count=self.__read_uint(4)
        self.__model.vertices=[self.__read_vertex() 
                for i in range(vertex_count)]

        ####################
        # indices
        ####################
        index_count=self.__read_uint(4)
        self.__model.indices=[self.__read_uint(self.vertex_index_size) 
                for i in range(index_count)]

        ####################
        # textures
        ####################
        texture_count=self.__read_uint(4)
        self.__model.textures=[self.__read_text() 
                for i in range(texture_count)]

        ####################
        # materials
        ####################
        material_count=self.__read_uint(4)
        self.__model.materials=[self.__read_material() 
                for i in range(material_count)]

        ####################
        # bones
        ####################
        bone_count=self.__read_uint(4)
        self.__model.bones=[self.__read_bone() 
                for i in range(bone_count)]

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

    def __read_uint(self, size):
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
        return common.Vector2(
                self.__unpack("f", 4), 
                self.__unpack("f", 4)
                )

    def __read_vector3(self):
        return common.Vector3(
                self.__unpack("f", 4), 
                self.__unpack("f", 4), 
                self.__unpack("f", 4)
                )

    def __read_rgba(self):
        return common.RGBA(
                self.__unpack("f", 4), 
                self.__unpack("f", 4), 
                self.__unpack("f", 4),
                self.__unpack("f", 4)
                )

    def __read_rgb(self):
        return common.RGB(
                self.__unpack("f", 4), 
                self.__unpack("f", 4), 
                self.__unpack("f", 4)
                )

    def __read_deform(self):
        deform_type=self.__unpack("B", 1)
        if deform_type==0:
            return Bdef1(self.__read_uint(self.bone_index_size))
        if deform_type==1:
            return Bdef2(
                    self.__read_uint(self.bone_index_size),
                    self.__read_uint(self.bone_index_size),
                    self.__unpack("f", 4)
                    )
        """
        if deform_type==2:
            return Bdef4(
                    self.__read_uint(self.bone_index_size),
                    self.__read_uint(self.bone_index_size),
                    self.__read_uint(self.bone_index_size),
                    self.__read_uint(self.bone_index_size),
                    self.__unpack("f", 4), self.__unpack("f", 4),
                    self.__unpack("f", 4), self.__unpack("f", 4)
                    )
        """
        raise ParseException("unknown deform type: {0}".format(deform_type))

    def __read_material(self):
        material=Material(
                name=self.__read_text(),
                english_name=self.__read_text(),
                diffuse_color=self.__read_rgb(),
                diffuse_alpha=self.__unpack("f", 4),
                specular_color=self.__read_rgb(),
                specular_factor=self.__unpack("f", 4),
                ambient_color=self.__read_rgb(),
                flag=self.__read_uint(1),
                edge_color=self.__read_rgba(),
                edge_size=self.__unpack("f", 4),
                texture_index=self.__read_uint(self.texture_index_size),
                sphia_texture_index=self.__read_uint(self.texture_index_size),
                sphia_mode=self.__read_uint(1),
                toon_sharing_flag=self.__read_uint(1),
                )
        if material.toon_sharing_flag==0:
            material.toon_texture_index=self.__read_uint(self.texture_index_size)
        elif material.toon_sharing_flag==1:
            material.toon_texture_index=self.__read_uint(1)
        else:
            raise ParseException("unknown toon_sharing_flag {0}".format(material.toon_sharing_flag))
        material.comment=self.__read_text()
        material.index_count=self.__read_uint(4)
        return material

    def __read_bone(self):
        return None

