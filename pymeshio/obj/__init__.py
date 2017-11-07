# coding: utf-8


class FaceVertex:
    __slots__=[
            'v', 'vt', 'vn',
            ]
    def __init__(self, **kw):
        self.v=None
        self.vt=None
        self.vn=None
        for k, v in kw.items():
            if k=="v":
                self.v=v
            elif k=="vt":
                self.vt=v
            elif k=="vn":
                self.vn=v
            else:
                raise RuntimeError("unknown type: "+k)


class Face(object):
    __slots__=[
            "vertex_references"
            ]
    def __init__(self):
        self.vertex_references=[]

    def __str__(self):
        return ("<obj.Face: {vertex_count}>".format(
            vertex_count=len(self.vertex_references)
            ))


class Material(object):
    __slots__=[
            "name",
            "faces",
            "s",

            "Ns",
            "Ka",
            "Kd",
            "Ks",
            "Ni",
            "d",
            "illum",
            ]
    def __init__(self, name):
        self.name=name
        self.faces=[]
        self.s=None
        self.Ns=None
        self.Ka=None
        self.Kd=None
        self.Ks=None
        self.Ni=None
        self.d=None
        self.illum=None


class Model(object):
    __slots__=[
            "path",
            "comment",
            "vertices",
            "uv",
            "normals",
            "materials",
            "mtl",
            "order",
            ]
    def __init__(self):
        self.path=""
        self.comment=b""
        self.vertices=[]
        self.uv=[]
        self.normals=[]
        self.materials=[]
        self.mtl=None

    def __str__(self):
        return ('<obj %s: %d vertices, %d materials %s>' % (
            self.comment.decode("cp932"),
            len(self.vertices),
            len(self.materials),
            (self.mtl)
            ))

    def add_v(self, v):
        self.vertices.append(v)

    def add_vt(self, vt):
        self.uv.append(vt)

    def add_vn(self, vn):
        self.normals.append(vn)

    def get_or_create_material(self, name):
        for material in self.materials:
            if material.name==name:
                return material

        material=Material(name)
        self.materials.append(material)
        return material

    def get_vertex(self, ref):
        return (self.vertices[ref[0]-1], 
                ref[1] and self.uv[ref[1]-1],
                ref[2] and self.normals[ref[2]-1]
                )

