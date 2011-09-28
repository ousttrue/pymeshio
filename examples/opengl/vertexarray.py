#!/usr/bin/python
# coding: utf-8

from OpenGL.GL import *

'''
頂点配列

====
属性
====
* 位置
'''
class VertexArray(object):
    def __init__(self, vertices):
        self.vertices=vertices

    def __str__(self):
        return "<VertexArray %d>" % len(self.vertices)

    def draw(self):
        # 位置属性
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices)
        # 描画
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices))
        # 後始末
        glDisableClientState(GL_VERTEX_ARRAY)



'''
頂点配列

====
属性
====
* 位置
* UV
'''
class VertexArrayWithUV(object):
    def __init__(self, vertices, uvarray):
        self.vertices=vertices
        self.uvarray=uvarray

    def __str__(self):
        return "<VertexArrayWithUV %d>" % len(self.vertices)

    def draw(self):
        # 位置属性
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices)
        # UV属性
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glTexCoordPointer(2, GL_FLOAT, 0, self.uvarray)
        # 描画
        triangle_count=int(len(self.vertices)/3)
        glDrawArrays(GL_TRIANGLES, 0, triangle_count)
        # 後始末
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)


'''
インデックス参照頂点配列

====
属性
====
* 位置
'''
class IndexedVertexArray(object):
    def __init__(self, vertices, indices):
        self.vertices=vertices
        self.indices=indices

    def draw(self):
        # 位置属性
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices)
        # indexによる描画
        glDrawElements(GL_TRIANGLES, len(self.indices),
                GL_UNSIGNED_INT, self.indices)
        # 後始末
        glDisableClientState(GL_VERTEX_ARRAY)


'''
インデックス参照頂点配列

====
属性
====
* 位置
* 色
'''
class IndexedVertexArrayWithColor(object):
    def __init__(self, vertices, colors, indices):
        self.vertices=vertices
        self.colors=colors
        self.indices=indices

    def draw(self):
        # 位置属性
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vertices)
        # 色属性
        glEnableClientState(GL_COLOR_ARRAY)
        glColorPointer(3, GL_FLOAT, 0, self.colors)
        # indexによる描画
        glDrawElements(GL_TRIANGLES, len(self.indices),
                GL_UNSIGNED_INT, self.indices)
        # 後始末
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

