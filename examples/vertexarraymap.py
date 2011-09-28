#!/usr/bin/python
# coding: utf-8

import numpy
import vertexarray


'''
頂点配列をマテリアル毎に分別する
'''
class VertexArrayMap(object):
    def __init__(self, materials):
        self.materials=materials
        self.vertexArrayMap={}

    def getVertexArray(self, material_index):
        material=self.materials[material_index]
        if not material in self.vertexArrayMap:
            vertexArray=vertexarray.VertexArray([])
            self.vertexArrayMap[material]=vertexArray
        return self.vertexArrayMap[material]

    def addTriangle(self, material_index, v0, v1, v2):
        vertexArray=self.getVertexArray(material_index)
        vertexArray.vertices.append(v0.x)
        vertexArray.vertices.append(v0.y)
        vertexArray.vertices.append(v0.z)
        vertexArray.vertices.append(v1.x)
        vertexArray.vertices.append(v1.y)
        vertexArray.vertices.append(v1.z)
        vertexArray.vertices.append(v2.x)
        vertexArray.vertices.append(v2.y)
        vertexArray.vertices.append(v2.z)

    def draw(self):
        for m, vertexArray in self.vertexArrayMap.items():
            m.begin()
            vertexArray.draw()
            m.end()

    def optimize(self):
        for v in self.vertexArrayMap.values():
            v.vertices=numpy.array(v.vertices, 'f') 


'''
頂点配列をマテリアル毎に分別する(UV付き)
'''
class VertexArrayMapWithUV(object):
    def __init__(self, materials):
        self.materials=materials
        self.vertexArrayWithUVMap={}

    def getVertexArray(self, material_index):
        material=self.materials[material_index]
        if not material in self.vertexArrayWithUVMap:
            vertexArray=vertexarray.VertexArrayWithUV([], [])
            self.vertexArrayWithUVMap[material]=vertexArray
        return self.vertexArrayWithUVMap[material]

    def addTriangle(self, material_index, v0, v1, v2, uv0, uv1, uv2):
        vertexArray=self.getVertexArray(material_index)
        vertexArray.vertices.append(v0.x)
        vertexArray.vertices.append(v0.y)
        vertexArray.vertices.append(v0.z)
        vertexArray.vertices.append(v1.x)
        vertexArray.vertices.append(v1.y)
        vertexArray.vertices.append(v1.z)
        vertexArray.vertices.append(v2.x)
        vertexArray.vertices.append(v2.y)
        vertexArray.vertices.append(v2.z)
        vertexArray.uvarray.append(uv0.x)
        vertexArray.uvarray.append(uv0.y)
        vertexArray.uvarray.append(uv1.x)
        vertexArray.uvarray.append(uv1.y)
        vertexArray.uvarray.append(uv2.x)
        vertexArray.uvarray.append(uv2.y)

    def draw(self):
        for m, vertexArray in self.vertexArrayWithUVMap.items():
            m.begin()
            vertexArray.draw()
            m.end()

    def optimize(self):
        for v in self.vertexArrayWithUVMap.values():
            v.vertices=numpy.array(v.vertices, 'f') 
            v.uvarray=numpy.array(v.uvarray, 'f') 

    def onInitialize(self):
        [m.onInitialize() for m in self.materials]

