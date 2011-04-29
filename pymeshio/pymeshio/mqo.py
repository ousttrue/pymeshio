#!BPY
""" 
Name: 'Metasequoia(.mqo)...'
Blender: 245
Group: 'Import'
Tooltip: 'Import from Metasequoia file format (.mqo)'
"""
__author__= 'ousttrue'
__url__ = ["http://gunload.web.fc2.com/blender/"]
__version__= '0.4 2009/11/25'
__bpydoc__= '''\

MQO Importer

This script imports a mqo file.

0.2 20080123: update.
0.3 20091125: modify for linux.
0.4 20100310: rewrite.
0.5 20100311: create armature from mikoto bone.
'''

import os
import sys
import math


class RGBA(object):
    __slots__=['r', 'g', 'b', 'a']
    def __init__(self, r=0, g=0, b=0, a=0):
        self.r=r
        self.g=g
        self.b=b
        self.a=a

class Vector3(object):
    __slots__=['x', 'y', 'z']
    def __init__(self, x=0, y=0, z=0):
        self.x=x
        self.y=y
        self.z=z

    def __str__(self):
        return "[%f, %f, %f]" % (self.x, self.y, self.z)

    def __sub__(self, rhs):
        return Vector3(self.x-rhs.x, self.y-rhs.y, self.z-rhs.z)

    def getSqNorm(self):
        return self.x*self.x + self.y*self.y + self.z*self.z

    def getNorm(self):
        return math.sqrt(self.getSqNorm())

    def normalize(self):
        factor=1.0/self.getNorm()
        self.x*=factor
        self.y*=factor
        self.z*=factor
        return self

    def to_a(self):
        return [self.x, self.y, self.z]

    @staticmethod
    def dot(lhs, rhs):
        return lhs.x*rhs.x + lhs.y*rhs.y + lhs.z*rhs.z

    @staticmethod
    def cross(lhs, rhs):
        return Vector3(
                lhs.y*rhs.z - rhs.y*lhs.z,
                lhs.z*rhs.x - rhs.z*lhs.x,
                lhs.x*rhs.y - rhs.x*lhs.y,
                )


class Vector2(object):
    __slots__=['x', 'y']
    def __init__(self, x=0, y=0):
        self.x=x
        self.y=y

    def __str__(self):
        return "[%f, %f]" % (self.x, self.y)

    def __sub__(self, rhs):
        return Vector3(self.x-rhs.x, self.y-rhs.y)

    @staticmethod
    def cross(lhs, rhs):
        return lhs.x*rhs.y-lhs.y*rhs.x


###############################################################################
# MQO loader
###############################################################################
class Material(object):
    __slots__=[
            "name", "shader", "color", "diffuse", 
            "ambient", "emit", "specular", "power",
            "tex",
            ]
    def __init__(self, name):
        self.name=name
        self.shader=3
        self.color=RGBA(0.5, 0.5, 0.5, 1.0)
        self.diffuse=1.0
        self.ambient=0.0
        self.emit=0.0
        self.specular=0.0
        self.power=5.0
        self.tex=""

    def getName(self): return self.name
    def getTexture(self): return self.tex

    def parse(self, line):
        offset=0
        while True:
            leftParenthesis=line.find("(", offset)
            if leftParenthesis==-1:
                break
            key=line[offset:leftParenthesis]
            rightParenthesis=line.find(")", leftParenthesis+1)
            if rightParenthesis==-1:
                raise ValueError("assert")

            param=line[leftParenthesis+1:rightParenthesis]
            if key=="shader":
                self.shader=int(param)
            elif key=="col":
                self.color=RGBA(*[float(e) for e in param.split()])
            elif key=="dif":
                self.diffuse=float(param)
            elif key=="amb":
                self.ambient=float(param)
            elif key=="emi":
                self.emit=float(param)
            elif key=="spc":
                self.specular=float(param)
            elif key=="power":
                self.power=float(param)
            elif key=="tex":
                self.tex=param[1:-1]
            else:
                print(
                        "%s#parse" % self.name, 
                        "unknown key: %s" %  key
                        )

            offset=rightParenthesis+2

    def __str__(self):
        return "<Material %s shader: %d [%f, %f, %f, %f] %f>" % (
                self.name, self.shader,
                self.color[0], self.color[1], self.color[2], self.color[3],
                self.diffuse)


class Obj(object):
    __slots__=["name", "depth", "folding", 
            "scale", "rotation", "translation",
            "visible", "locking", "shading", "facet",
            "color", "color_type", "mirror", "mirror_axis",
            "vertices", "faces", "edges", "smoothing",
            ]

    def __init__(self, name):
        self.name=name
        self.vertices=[]
        self.faces=[]
        self.edges=[]
        self.depth=0
        self.folding=0
        self.scale=[1, 1, 1]
        self.rotation=[0, 0, 0]
        self.translation=[0, 0, 0]
        self.visible=15
        self.locking=0
        self.shading=0
        self.facet=59.5
        self.color=[1, 1, 1]
        self.color_type=0
        self.mirror=0
        self.smoothing=0

    def getName(self): return self.name

    def addVertex(self, x, y, z):
        self.vertices.append(Vector3(x, y, z))

    def addFace(self, face):
        if face.index_count==2:
            self.edges.append(face)
        else:
            self.faces.append(face)

    def __str__(self):
        return "<Object %s, %d vertices, %d faces>" % (
                self.name, len(self.vertices), len(self.faces))


class Face(object):
    __slots__=[
            "index_count",
            "indices", "material_index", "col", "uv",
            ]
    def __init__(self, index_count, line):
        if index_count<2 or index_count>4:
            raise ValueError("invalid vertex count: %d" % index_count)
        self.material_index=0
        self.col=[]
        self.uv=[Vector2(0, 0)]*4
        self.index_count=index_count
        offset=0
        while True:
            leftParenthesis=line.find("(", offset)
            if leftParenthesis==-1:
                break
            key=line[offset:leftParenthesis]
            rightParenthesis=line.find(")", leftParenthesis+1)
            if rightParenthesis==-1:
                raise ValueError("assert")
            params=line[leftParenthesis+1:rightParenthesis].split()
            if key=="V":
                self.indices=[int(e) for e in params]
            elif key=="M":
                self.material_index=int(params[0])
            elif key=="UV":
                uv_list=[float(e) for e in params]
                self.uv=[]
                for i in range(0, len(uv_list), 2):
                    self.uv.append(Vector2(uv_list[i], uv_list[i+1]))
            elif key=="COL":
                for n in params:
                    d=int(n)
                    # R
                    d, m=divmod(d, 256)
                    self.col.append(m)
                    # G
                    d, m=divmod(d, 256)
                    self.col.append(m)
                    # B
                    d, m=divmod(d, 256)
                    self.col.append(m)
                    # A
                    d, m=divmod(d, 256)
                    self.col.append(m)
            else:
                print("Face#__init__:unknown key: %s" % key)

            offset=rightParenthesis+2

    def getIndex(self, i): return self.indices[i]
    def getUV(self, i): return self.uv[i] if i<len(self.uv) else Vector2(0, 0)


def withio(method):
    def new(self, path):
        self.io=open(path, encoding='cp932')
        result=method(self)
        self.io=None
        return result
    return new


class IO(object):
    __slots__=[
            "has_mikoto",
            "eof", "io", "lines",
            "materials", "objects",
            ]
    def __init__(self):
        self.has_mikoto=False
        self.eof=False
        self.io=None
        self.lines=0
        self.materials=[]
        self.objects=[]

    def __str__(self):
        return "<MQO %d lines, %d materials, %d objects>" % (
                self.lines, len(self.materials), len(self.objects))

    def getline(self):
        line=self.io.readline()
        self.lines+=1
        if line=="":
            self.eof=True
            return None
        return line.strip()

    def printError(self, method, msg):
        print("%s:%s:%d" % (method, msg, self.lines))

    @withio
    def read(self):
        line=self.getline()
        if line!="Metasequoia Document":
            print("invalid signature")
            return False

        line=self.getline()
        if line!="Format Text Ver 1.0":
            print("unknown version: %s" % line)

        while True:
            line=self.getline()
            if line==None:
                # eof
                break;
            if line=="":
                # empty line
                continue

            tokens=line.split()
            key=tokens[0]

            if key=="Eof":
                return True
            elif key=="Scene":
                if not self.readChunk():
                    return False
            elif key=="Material":
                if not self.readMaterial():
                    return False
            elif key=="Object":
                firstQuote=line.find('"')
                secondQuote=line.find('"', firstQuote+1)
                if not self.readObject(line[firstQuote+1:secondQuote]):
                    return False
            elif key=="BackImage":
                if not self.readChunk():
                    return False
            elif key=="IncludeXml":
                firstQuote=line.find('"')
                secondQuote=line.find('"', firstQuote+1)
                print("IncludeXml", line[firstQuote+1:secondQuote])
            else:
                print("unknown key: %s" % key)
                if not self.readChunk():
                    return False

        self.printError("parse", "invalid eof")
        return False

    def readObject(self, name):
        obj=Obj(name)
        if name.startswith('bone'):
            self.has_mikoto=True
        self.objects.append(obj)
        while(True):
            line=self.getline()
            if line==None:
                # eof
                break;
            if line=="":
                # empty line
                continue

            if line=="}":
                return True
            else:
                tokens=line.split()
                key=tokens[0]
                if key=="vertex":
                    if not self.readVertex(obj):
                        return False
                elif key=="face":
                    if not self.readFace(obj):
                        return False
                elif key=="depth":
                    obj.depth=int(tokens[1])
                else:
                    print(
                            "%s#readObject" % name,
                            "unknown key: %s" % name
                            )

        self.printError("readObject", "invalid eof")
        return False

    def readFace(self, obj):
        while(True):
            line=self.getline()
            if line==None:
                # eof
                break;
            if line=="":
                # empty line
                continue

            if line=="}":
                return True
            else:
                # face
                tokens=line.split(' ', 1)
                try:
                    obj.addFace(Face(int(tokens[0]), tokens[1]))
                except ValueError as ex:
                    self.printError("readFace", ex)
                    #return False

        self.printError("readFace", "invalid eof")
        return False

    def readVertex(self, obj):
        while(True):
            line=self.getline()
            if line==None:
                # eof
                break;
            if line=="":
                # empty line
                continue

            if line=="}":
                return True
            else:
                # vertex
                obj.addVertex(*[float(v) for v in line.split()])

        self.printError("readVertex", "invalid eof")
        return False

    def readMaterial(self):
        while(True):
            line=self.getline()
            if line==None:
                # eof
                break;
            if line=="":
                # empty line
                continue

            if line=="}":
                return True
            else:
                # material
                secondQuaote=line.find('"', 1)                
                material=Material(line[1:secondQuaote])
                try:
                    material.parse(line[secondQuaote+2:])
                except ValueError as ex:
                    self.printError("readMaterial", ex)

                self.materials.append(material)

        self.printError("readMaterial", "invalid eof")
        return False

    def readChunk(self):
        level=1
        while(True):
            line=self.getline()
            if line==None:
                # eof
                break;
            if line=="":
                # empty line
                continue

            if line=="}":
                level-=1
                if level==0:
                    return True
            elif line.find("{")!=-1:
                level+=1

        self.printError("readChunk", "invalid eof")
        return False

