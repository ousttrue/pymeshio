from logging import getLogger
logger = getLogger(__name__)

import ctypes
import array
import pathlib

import pymeshio.ctypesmath
from pymeshio.common import BytesReader
from pymeshio.skinnedmesh import MetaData, Direction, Coordinate, Submesh, Model


class PmdVertex(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("pos", pymeshio.ctypesmath.Vec3),
        ("normal", pymeshio.ctypesmath.Vec3),
        ("uv", pymeshio.ctypesmath.Vec2),
        ("bone0", ctypes.c_int16),
        ("bone1", ctypes.c_int16),
        ("weight0", ctypes.c_byte),
        ("flag", ctypes.c_byte),
    ]


assert ctypes.sizeof(PmdVertex) == 38


class PmdMaterial(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('color', pymeshio.ctypesmath.Vec4),
        ('specularity', ctypes.c_float),
        ('specular', pymeshio.ctypesmath.Vec3),
        ('ambient', pymeshio.ctypesmath.Vec3),
        ('toon_index', ctypes.c_byte),
        ('flag', ctypes.c_byte),
        ('index_count', ctypes.c_uint32),
        ('texture', ctypes.c_char * 20),
    ]


assert ctypes.sizeof(PmdMaterial) == 70


def load_bytes(data: bytes, path: pathlib.Path)->Model:
    # header
    r = BytesReader(data)
    if r.get_bytes(3) != b'Pmd':
        return None

    version = r.get_float()
    if version != 1.0:
        return None

    name = r.get_str(20, 'cp932')
    logger.debug(name)
    comment = r.get_str(256, 'cp932')
    logger.debug(comment)

    # vertices
    vertex_count = r.get_uint32()
    vertices_bytes = r.get_bytes(vertex_count * ctypes.sizeof(PmdVertex))
    vertices = (PmdVertex * vertex_count).from_buffer_copy(vertices_bytes)
    logger.debug('%d vertices. %d bytes', vertex_count, len(vertices))

    # indices
    index_count = r.get_uint32()
    indices = array.array('H')
    indices.frombytes(r.get_bytes(
        index_count * ctypes.sizeof(ctypes.c_uint16)))
    logger.debug('%d indices. %d bytes', index_count,
                 indices.itemsize * len(indices))

    # materials
    material_count = r.get_uint32()
    materials_bytes = r.get_bytes(material_count * ctypes.sizeof(PmdMaterial))
    materials = (PmdMaterial * material_count).from_buffer_copy(materials_bytes)
    logger.debug('%d materials. %d bytes', material_count, len(materials))

    metadata = MetaData(
        path, name, comment,
        Coordinate.YUP_ZFORWARD,
        Direction.Y_POSITIVE,
        Direction.Z_NEGATIVE,
        Direction.X_NEGATIVE,
        1.58 / 20
    )

    def PmdMaterial_to_submesh(i: int, material: PmdMaterial)->Submesh:
        return Submesh(
            name=f'material{i}',
            index_count=material.index_count,
            material=material,
        )

    return Model(metadata, indices, vertices,
                       [PmdMaterial_to_submesh(i, x) for i, x in enumerate(materials)])
