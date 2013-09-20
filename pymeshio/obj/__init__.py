# coding: utf-8


class Model(object):
    __slots__=[
            "path",
            "comment",
            "vertices",
            "uv",
            "normals",
            ]
    def __init__(self):
        self.path=""
        self.comment=b""
        self.vertices=[]
        self.uv=[]
        self.normals=[]

    def __str__(self):
        return ('<obj %s: %d vertices>' % (
            self.comment.decode("cp932"),
            len(self.vertices)
            ))

