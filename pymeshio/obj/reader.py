# coding: utf-8
"""
obj reader
"""
import io
from .. import obj
from .. import common


class Reader(common.TextReader):
    """mqo reader
    """
    __slots__=[
            "has_mikoto",
            "materials", "objects",
            "vertices",
            "normals",
            "uv",
            ]
    def __init__(self, ios):
        super(Reader, self).__init__(ios)
        self.vertices=[]
        self.normals=[]
        self.uv=[]

    def __str__(self):
        return "<Obj %d lines, %d vertices, %d materials>" % (
                self.lines, len(self.vertices), len(self.materials))

    def read(self):
        line=self.getline()
        if not line.startswith(b"#"):
            # is not obj file
            return

        model=obj.Model()

        while True:
            line=self.getline()
            if not line:
                break
            line=line.strip()
            if line=="":
                break
            token=line.split()
            if token[0]==b"v":
                self.vertices.append(common.Vector3(
                    float(token[1]),
                    float(token[2]),
                    float(token[3])
                    ))
            elif token[0]==b"vt":
                self.uv.append(common.Vector2(
                    float(token[1]),
                    float(token[2]),
                    ))
            elif token[0]==b"vn":
                self.normals.append(common.Vector3(
                    float(token[1]),
                    float(token[2]),
                    float(token[3])
                    ))
            elif token[0]==b"g":
                pass
            elif token[0]==b"f":
                pass
            elif token[0]==b"usemtl":
                pass
            else:
                print(b"unknown key: "+token[0])


        return model


def read_from_file(path):
    """
    read from file path, then return the pymeshio.mqo.Model.

    :Parameters:
      path
        file path
    """
    with io.open(path, 'rb') as ios:
        return read(ios)


def read(ios):
    """
    read from ios, then return the pymeshio.mqo.Model.

    :Parameters:
      ios
        input stream (in io.IOBase)
    """
    assert(isinstance(ios, io.IOBase))
    return Reader(ios).read()

