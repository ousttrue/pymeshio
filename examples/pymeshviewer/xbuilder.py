#!/usr/bin/env python
# coding: utf-8

import time
import os
import pymeshio.x.reader
import opengl.material
import opengl.texture
import opengl.vertexarraymap


def build(path):
    t=time.time()
    model=pymeshio.x.reader.read_from_file(path)
    if not model:
        return
    print(time.time()-t, "sec")
    print(model)

    # build
    basedir=os.path.dirname(path)
    indexedVertexArray=opengl.vertexarray.IndexedVertexArray()
    for v, n, c in zip(model.vertices, model.normals, model.uvs):
        # left-handed y-up to right-handed y-up                
        indexedVertexArray.addVertex(
                (v.x, v.y, -v.z, 1), 
                (n.x, n.y, -n.z), # normal
                (c.x, c.y), # uv 
                (1, 1, 1, 1), # color
                0, 0, 0 # b0, b1, w0
                )

    # faces
    for i, m in enumerate(model.materials):
        print(m)
        material=opengl.material.MQOMaterial()
        material.vcol=False
        material.rgba=(
                m.diffuse.a, 
                m.diffuse.g, 
                m.diffuse.b, 
                m.diffuse.a
                )
        indices=indexedVertexArray.addMaterial(material)
        for f, mi in zip(model.faces, model.face_materials):
            if i==mi:
                if len(f)==3:
                    indices+=f
                elif len(f)==4:
                    indices+=[f[0], f[1], f[2], f[2], f[3], f[0]]
                else:
                    assert(False)

    return indexedVertexArray

