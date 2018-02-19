from enum import Enum
import pathlib


class Direction(Enum):
    X_POSITIVE = 0
    X_NEGATIVE = 1
    Y_POSITIVE = 2
    Y_NEGATIVE = 3
    Z_POSITIVE = 4
    Z_NEGATIVE = 5


class Coordinate(Enum):
    YUP_ZFORWARD = 0 # DirectX, Unity
    YUP_ZBACKWARD = 1 # OpenGL
    ZUP_YFORWARD = 2 # Blender


class MetaData:
    def __init__(self, path: pathlib.Path, name: str, comment: str,
                 coord: Coordinate,
                 up: Direction,
                 forward: Direction,
                 right: Direction,
                 to_meter=1.0)->None:
        self.path = path.absolute()
        self.name = name
        self.comment = comment
        self.coord = coord
        self.forward = forward
        self.up = up
        self.right = right
        self.to_meter = to_meter

    @property
    def base_path(self):
        return self.path.parent
