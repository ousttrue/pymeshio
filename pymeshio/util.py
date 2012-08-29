# coding: utf-8
import sys
import os

from . import pmx
from .pmx import reader as pmx_reader
pmx.reader=pmx_reader


class Face(object):
    __slots__=['indices', 'material_index']
    def __init__(self):
        self.indices=[]
        self.material_index=0


def convert_coord(xyz):
    """
    Left handed y-up to Right handed z-up
    """
    # swap y and z
    tmp=xyz.y
    xyz.y=xyz.z
    xyz.z=tmp
    return xyz


class Mesh(object):
    __slots__=[
            'vertices', 'faces',
            ]
    def __init__(self):
        self.vertices=[]
        self.faces=[]

    def convert_coord(self):
        for v in self.vertices:
            v.position=convert_coord(v.position)
            v.normal=convert_coord(v.normal)


class GenericModel(object):
    __slots__=[
            'filepath',
            'name', 'english_name',
            'comment', 'english_comment',
            'meshes', 'materials', 'textures',
            'bones',
            ]

    def __init__(self):
        self.filepath=None
        self.name=None
        self.english_name=None
        self.comment=None
        self.english_comment=None
        self.meshes=[]
        self.materials=[]


    def convert_coord(self):
        for b in self.bones:
            b.position=convert_coord(b.position)
            b.tail_position=convert_coord(b.tail_position)

        for m in self.meshes:
            m.convert_coord()


    def load_pmx(self, src):
        mesh=Mesh()
        self.meshes.append(mesh)

        self.filepath=src.path
        self.name=src.name
        self.english_name=src.english_name
        self.comment=src.english_name
        self.english_comment=src.english_comment

        # vertices
        mesh.vertices=src.vertices[:]

        # textures
        self.textures=src.textures[:]

        # materials
        self.materials=src.materials[:]

        # faces
        def indices():
            for i in src.indices:
                yield i
        it=indices()
        for i, m in enumerate(src.materials):
            for _ in range(0, m.vertex_count, 3):
                face=Face()
                face.indices=[next(it), next(it), next(it)]
                face.material_index=i
                mesh.faces.append(face)

        # bones
        self.bones=src.bones[:]

    @staticmethod
    def read_from_file(filepath):
        if not os.path.exists(filepath):
            return

        stem, ext=os.path.splitext(filepath)
        ext=ext.lower()

        model=GenericModel()
        if ext==".pmd":
            from . import pmd
            import pmd.reader
            m=pmd.reader.read_from_file(filepath)

        elif ext==".pmx":
            m=pmx.reader.read_from_file(filepath)
            if not m:
                return
            model.load_pmx(m)
            # left handed Y-up to right handed Z-up
            model.convert_coord()

        elif ext==".mqo":
            from . import mqo
            import mqo.reader
            m=mqo.reader.read_from_file(filepath)

        else:
            print('unknown file type: '+ext)
            return

        return model

