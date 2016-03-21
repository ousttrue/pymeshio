#!/usr/bin/python
# coding: utf-8

from OpenGL.GL import *
import ctypes

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

    def get_boundingbox(self):
        vertices_size=len(self.vertices)
        if(vertices_size==0):
            return ([0, 0, 0], [0, 0, 0])
        def vertex_gen_factory():
            for i in range(0, vertices_size, 3):
                yield [
                        self.vertices[i],
                        self.vertices[i+1],
                        self.vertices[i+2]
                        ]
        vertex_gen=vertex_gen_factory()
        v=next(vertex_gen)
        max_v=v[:]
        min_v=v[:]
        for v in vertex_gen:
            min_v[0]=min(min_v[0], v[0]) 
            min_v[1]=min(min_v[1], v[1]) 
            min_v[2]=min(min_v[2], v[2]) 
            max_v[0]=max(max_v[0], v[0]) 
            max_v[1]=max(max_v[1], v[1]) 
            max_v[2]=max(max_v[2], v[2]) 
        return (min_v, max_v)

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
        self.indices=[]
        self.buffers=[]

    def addVertex(self, pos, normal, uv, color, b0, b1, w0):
        self.vertices+=pos
        self.normal+=normal
        self.colors+=color
        self.uvlist+=uv
        self.b0.append(b0)
        self.b1.append(b1)
        self.w0.append(w0)

    def setIndices(self, indices):
        self.indices=indices

    def addMaterial(self, material):
        self.materials.append(material)

    def create_array_buffer(self, buffer_id, floats):
        print('create_array_buuffer', buffer_id)
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        glBufferData(GL_ARRAY_BUFFER, 
                len(floats)*4,  # byte size
                (ctypes.c_float*len(floats))(*floats), # 謎のctypes
                GL_STATIC_DRAW)

    def create_vbo(self):
        self.buffers = glGenBuffers(4+1)
        #print("create_vbo", self.buffers)

        self.create_array_buffer(self.buffers[0], self.vertices)
        self.create_array_buffer(self.buffers[1], self.normal)
        self.create_array_buffer(self.buffers[2], self.colors)
        self.create_array_buffer(self.buffers[3], self.uvlist)

        # indices
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.buffers[4])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 
                len(self.indices)*4, # byte size
                (ctypes.c_uint*len(self.indices))(*self.indices),  # 謎のctypes
                GL_STATIC_DRAW)

    def draw(self):
        if len(self.buffers)==0:
            self.create_vbo()

        glEnableClientState(GL_VERTEX_ARRAY);
        glBindBuffer(GL_ARRAY_BUFFER, self.buffers[0]);
        glVertexPointer(4, GL_FLOAT, 0, None);

        glEnableClientState(GL_NORMAL_ARRAY);
        glBindBuffer(GL_ARRAY_BUFFER, self.buffers[1]);
        glNormalPointer(GL_FLOAT, 0, None);

        #glEnableClientState(GL_COLOR_ARRAY);
        #glBindBuffer(GL_ARRAY_BUFFER, self.buffers[2]);
        #glColorPointer(4, GL_FLOAT, 0, None);

        glEnableClientState(GL_TEXTURE_COORD_ARRAY);
        glBindBuffer(GL_ARRAY_BUFFER, self.buffers[3]);
        glTexCoordPointer(2, GL_FLOAT, 0, None);

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.buffers[4]);
        index_offset=0
        for i, m in enumerate(self.materials):
            # submesh
            m.begin()
            glDrawElements(GL_TRIANGLES, m.vertex_count, GL_UNSIGNED_INT, ctypes.c_void_p(index_offset));
            index_offset+=m.vertex_count * 4 # byte size
            m.end()

        # cleanup
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY);
        glDisableClientState(GL_VERTEX_ARRAY)

    def optimize(self):
        self.vertices=numpy.array(self.vertices, numpy.float32) 
        self.uvlist=numpy.array(self.uvlist, numpy.float32) 
        for m, indices in self.indicesMap.items():
            self.indicesMap[m]=numpy.array(indices, numpy.uint32)

    def get_boundingbox(self):
        vertices_size=len(self.vertices)
        if(vertices_size==0):
            return ([0, 0, 0], [0, 0, 0])
        def vertex_gen_factory():
            for i in range(0, vertices_size, 4):
                yield [
                        self.vertices[i],
                        self.vertices[i+1],
                        self.vertices[i+2]
                        ]
        vertex_gen=vertex_gen_factory()
        v=next(vertex_gen)
        max_v=v[:]
        min_v=v[:]
        for v in vertex_gen:
            if v[0]<min_v[0]:
                min_v[0]=v[0]
            if v[1]<min_v[1]:
                min_v[1]=v[1]
            if v[2]<min_v[2]:
                min_v[2]=v[2]
            if v[0]>max_v[0]:
                max_v[0]=v[0]
            if v[1]>max_v[1]:
                max_v[1]=v[1]
            if v[2]>max_v[2]:
                max_v[2]=v[2]
        return (min_v, max_v)
