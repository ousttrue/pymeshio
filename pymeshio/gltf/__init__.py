import json
from typing import NamedTuple, List, Any
import ctypes
import pathlib


class Material:
    def __init__(self)->None:
        pass


class Submesh:
    def __init__(self)->None:
        self.material = None
        self.index_count = None


class Float3(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float)
    ]


class BufferView(NamedTuple):
    buffer: int
    byteOffset: int
    byteLength: int
    target: int


def component_byte_length(component_type: int)->int:
    if component_type == 5123:
        return 2  # UINT16
    elif component_type == 5126:
        return 4  # Float
    else:
        raise GltfException(f'unknown component_type: {component_type}')


def element_count(element_type: str)->int:
    if element_type == "SCALAR":
        return 1
    elif element_type == "VEC3":
        return 3
    else:
        raise GltfException(f'unknown element type: {element_type}')


class Accessor(NamedTuple):
    bufferView: int
    byteOffset: int
    componentType: int
    type: str
    count: int
    min: List[Any]
    max: List[Any]

    @property
    def byteLength(self)->int:
        return component_byte_length(self.componentType) * element_count(self.type) * self.count


class BinaryAccessor:
    def __init__(self, here: pathlib.Path)->None:
        self.here = here
        self.buffers: List[bytes] = []
        self.views: List[BufferView] = None
        self.accessors: List[Accessor] = None

    def load(self, buffers: List[Any], views: List[Any], accessors: List[Any])->None:
        self.buffers.clear()
        for x in buffers:
            uri = self.here / x['uri']
            data = uri.read_bytes()
            if len(data) != x['byteLength']:
                raise GltfException('invalid size')
            self.buffers.append(data)

        self.views = [BufferView(**x) for x in views]
        self.accessors = [Accessor(**x) for x in accessors]

    def get_buffer(self, accessor_index: int, array_type)->bytes:
        accessor = self.accessors[accessor_index]
        view = self.views[accessor.bufferView]
        buffer = self.buffers[view.buffer]
        start = view.byteOffset + accessor.byteOffset
        end = start + accessor.byteLength
        segment = buffer[start:end]
        return (array_type * accessor.count).from_buffer_copy(segment)

    def get_positions(self, accessor_index: int)->ctypes.Array:
        return self.get_buffer(accessor_index, Float3)

    def get_indices(self, accessor_index: int)->ctypes.Array:
        return self.get_buffer(accessor_index, ctypes.c_ushort)


class GltfException(Exception): pass


class Primitive:
    def __init__(self)->None:
        self.positions = None
        self.normals = None
        self.uv = None
        self.indices = None
        self.boneweights = None
        self.material = None

    def load(self, primitive, binary: BinaryAccessor)->None:
        attribs = primitive['attributes']
        index = primitive['indices']

        for k, v in attribs.items():

            if k == 'POSITION':
                self.positions = binary.get_positions(v)
                #logger.debug('%d vertices', len(self.positions))
            else:
                raise GltfException(f'unknown attribute: {k}')

        self.indices = binary.get_indices(index)
        #logger.debug('%d indices', len(self.indices))


class Mesh:
    def __init__(self)->None:
        self.primitives: List[Primitive] = []

    def load(self, primitives, binary: BinaryAccessor)->None:
        for x in primitives:
            prim = Primitive()
            prim.load(x, binary)
            self.primitives.append(prim)


class Gltf:
    def __init__(self, here: pathlib.Path)->None:
        self.here = here
        self.json: Any = None
        self.meshes: List[Mesh] = []
        self.binary = BinaryAccessor(self.here)

    @property
    def version(self):
        return self.json['asset']['version']

    def load_from_json(self, src: str)->None:
        self.json = json.loads(src)

        self.binary.load(
            self.json['buffers'], self.json['bufferViews'], self.json['accessors'])

        for x in self.json['meshes']:
            mesh = Mesh()
            mesh.load(x['primitives'], self.binary)
            self.meshes.append(mesh)
