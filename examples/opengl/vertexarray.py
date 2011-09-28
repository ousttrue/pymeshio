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
* UV
'''
class IndexedVertexArray(object):
    def __init__(self):
        # vertices
        self.vertices=[]
        self.normal=[]
        self.colors=[]
        self.uvlist=[]
        self.b0=[]
        self.b1=[]
        self.w0=[]
        # indices
        self.materials=[]
        self.indicesMap={}

    def addVertex(self, pos, normal, color, uv, b0, b1, w0):
        self.vertices+=pos
        self.normal+=normal
        self.colors+=color
        self.uvlist+=uv
        self.b0.append(b0)
        self.b1.append(b1)
        self.w0.append(w0)

    def addMaterial(self, material):
        self.materials.append(material)
        indices=[]
        self.indicesMap[material]=indices
        return indices

    def draw(self):
        # 位置属性
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(4, GL_FLOAT, 0, self.vertices)
        # マテリアル毎の描画
        for m in self.materials:
            # 順序維持
            indices=self.indicesMap[m]
            # indexによる描画
            glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, indices)
        # 後始末
        glDisableClientState(GL_VERTEX_ARRAY)

    def optimize(self):
        pass
        #for v in self.vertexArrayMap.values():
        #    v.vertices=numpy.array(v.vertices, 'f') 

