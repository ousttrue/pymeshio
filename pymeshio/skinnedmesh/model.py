'''
Standard skinned mesh model.

* 4 weight bone skinning

'''

import ctypes
import array
from typing import NamedTuple, List, Any

from pymeshio.ctypesmath import Vec3
from .metadata import MetaData


class BoneWeight(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("bone0", ctypes.c_ushort),
        ("bone1", ctypes.c_ushort),
        ("bone2", ctypes.c_ushort),
        ("bone3", ctypes.c_ushort),
        ("weight0", ctypes.c_float),
        ("weight1", ctypes.c_float),
        ("weight2", ctypes.c_float),
        ("weight3", ctypes.c_float),
    ]


class Submesh(NamedTuple):
    name: str
    index_count: int
    material: Any


class Model:
    def __init__(self, metadata: MetaData,
                 indices: array.array,
                 vertices: ctypes.Array,
                 submeshes: List[Submesh])->None:
        self.metadata = metadata
        self.indices = indices
        self.vertices = vertices
        self.submeshes = submeshes

    def __repr__(self)->str:
        return f'{{Pmd {self.metadata.name}}}'

    def meter_scale(self)->None:
        to_meter = self.metadata.to_meter
        for i in range(len(self.vertices)):
            self.vertices[i].pos[0] *= to_meter
            self.vertices[i].pos[1] *= to_meter
            self.vertices[i].pos[2] *= to_meter
