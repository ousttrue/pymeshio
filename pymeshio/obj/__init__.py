# coding: utf-8


class Face(object):
    __slots__=[
            "position",
            "uv",
            "normal",
            ]
    def __init__(self):
        self.position=[]
        self.uv=[]
        self.normal=[]

    def __str__(self):
        return ("<obj.Face: pos{pos}, uv{uv}, normal{normal}>".format(
            pos=self.position,
            uv=self.uv,
            normal=self.normal
            ))

    def push(self, args):
        # position
        self.position.append(int(args[0]))

        # uv
        try:
            self.uv.append(int(args[1]))
        except ValueError:
            self.uv.append(0)

        # normal
        try:
            self.normal.append(int(args[2]))
        except IndexError:
            self.normal.append(0)

    def to_zero_origin(self):
        """
        1 origin を 0 originに修正する
        """
        self.position=[n-1 if n>0 else 0 for n in self.position]
        self.uv=[n-1 if n>0 else 0 for n in self.uv]
        self.normal=[n-1 if n>0 else 0 for n in self.normal]


class Model(object):
    __slots__=[
            "path",
            "comment",
            "vertices",
            "uv",
            "normals",
            "faces",
            ]
    def __init__(self):
        self.path=""
        self.comment=b""
        self.vertices=[]
        self.uv=[]
        self.normals=[]
        self.faces=[]

    def __str__(self):
        return ('<obj %s: %d vertices, %d faces>' % (
            self.comment.decode("cp932"),
            len(self.vertices),
            len(self.faces)
            ))

