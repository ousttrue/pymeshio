# coding: utf-8
import sys
import os

from . import pmx
import pmx.reader


class Material(object):
    __slots__=[
            'name',
            ]
    def __init__(self, name):
        self.name=name


class Vector2(object):
    __slots__=[
            'x', 'y',
            ]
    def __init__(self, x, y):
        self.x=x
        self.y=y


class Vector3(object):
    __slots__=[
            'x', 'y', 'z'
            ]
    def __init__(self, x, y, z):
        self.x=x
        self.y=y
        self.z=z


class Vertex(object):
    __slots__=[
            'pos',
            'normal',
            'uv',
            'skinning',
            ]
    def __init__(self, pos, uv, normal=None, skinning=None):
        self.pos=pos
        self.uv=uv
        self.normal=normal
        self.skinning=skinning


class Mesh(object):
    __slots__=[
            'vertices', 'faces',
            ]
    def __init__(self):
        pass


class GenericModel(object):
    __slots__=[
            'meshes',
            ]

    def __init__(self):
        self.meshes=[]

    def load_pmx(self, src):
        mesh=Mesh()
        def parse_pmx_vertex(v):
            if isinstance(v.deform, pmx.Bdef1):
                skinning=[(v.deform.index0, 1.0)]
            elif isinstance(v.deform, pmx.Bdef2):
                skinning=[
                        (v.deform.index0, v.deform.weight0), 
                        (v.deform.index1, 1.0-v.deform.weight0)
                        ]
            else:
                raise 'unknown deform !'
            vertex=Vertex(
                    pos=Vector3(v.position.x, v.position.y, v.position.z),
                    uv=Vector2(v.uv.x, v.uv.y),
                    normal=Vector3(v.normal.x, v.normal.y, v.normal.z),
                    skinning=skinning)
            return vertex
        mesh.vertices=[parse_pmx_vertex(v) for v in src.vertices]
        self.meshes.append(mesh)


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

        elif ext==".mqo":
            from . import mqo
            import mqo.reader
            m=mqo.reader.read_from_file(filepath)

        else:
            print('unknown file type: '+ext)
            return

        return model

