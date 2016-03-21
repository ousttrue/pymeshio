#!/usr/bin/python
# coding: utf-8


from . import vertexarray


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
    def __init__(self):
        self.materials=[]
        self.vertexArrayWithUVMap={}

    def addMaterial(self, material):
        self.materials.append(material)
        self.vertexArrayWithUVMap[material]=vertexarray.VertexArrayWithUV([], [])

    def getVertexArray(self, material_index):
        material=self.materials[material_index]
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
        #[m.onInitialize() for m in self.materials]
        pass

    def get_boundingbox(self):
        if len(self.vertexArrayWithUVMap)==0:
            return ([0, 0, 0], [0, 0, 0])

        gen=iter(self.vertexArrayWithUVMap.values())
        (min_v, max_v)=next(gen).get_boundingbox()
        for va in gen:
            (va_min_v, va_max_v)=va.get_boundingbox()
            min_v[0]=min(min_v[0], va_min_v[0]) 
            min_v[1]=min(min_v[1], va_min_v[1]) 
            min_v[2]=min(min_v[2], va_min_v[2]) 
            max_v[0]=max(max_v[0], va_max_v[0]) 
            max_v[1]=max(max_v[1], va_max_v[1]) 
            max_v[2]=max(max_v[2], va_max_v[2]) 
        return (min_v, max_v)
