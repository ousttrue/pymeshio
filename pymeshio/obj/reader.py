# coding: utf-8
"""
obj reader
"""
import io
import sys
from .. import obj
from .. import common



class Reader(common.TextReader):
    """mqo reader
    """
    __slots__=[
            "has_mikoto",
            "materials", "objects",
            ]
    def __init__(self, ios):
        super(Reader, self).__init__(ios)

    def __str__(self):
        return "<Obj %d lines, %d vertices, %d materials>" % (
                self.lines, len(self.vertices), len(self.materials))

    def read(self):
        model=obj.Model()
        while True:
            line=self.getline()
            if not line:
                break

            line=line.strip()
            if line==b"":
                break

            if line[0]==ord("#"):
                if model.comment=="":
                    model.comment=line[1:].strip()
                continue

            token=line.split()
            if token[0]==b"v":
                model.vertices.append(common.Vector3(
                    float(token[1]),
                    float(token[2]),
                    float(token[3])
                    ))
            elif token[0]==b"vt":
                model.uv.append(common.Vector2(
                    float(token[1]),
                    float(token[2]),
                    ))
            elif token[0]==b"vn":
                model.normals.append(common.Vector3(
                    float(token[1]),
                    float(token[2]),
                    float(token[3])
                    ))
            elif token[0]==b"g":
                pass
            elif token[0]==b"f":
                model.faces.append(self.parseFace(*token[1:]))
            elif token[0]==b"mtllib":
                pass
            elif token[0]==b"usemtl":
                pass
            else:
                print(b"unknown key: "+line)

        return model
    
    def parseFace(self, *faces):
        face=obj.Face()
        for f in faces:
            face.push(f.split(b"/"))
        return face


def read_from_file(path):
    """
    read from file path, then return the pymeshio.mqo.Model.

    :Parameters:
      path
        file path
    """
    with io.open(path, 'rb') as ios:
        model=read(ios)
        if model:
            model.path=path
            return model


def read(ios):
    """
    read from ios, then return the pymeshio.mqo.Model.

    :Parameters:
      ios
        input stream (in io.IOBase)
    """
    assert(isinstance(ios, io.IOBase))
    return Reader(ios).read()

