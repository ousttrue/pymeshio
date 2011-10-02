#!/usr/bin/env python
# coding: utf-8

import time
import os
import pymeshio.pmx.reader
import opengl.material
import opengl.texture
import opengl.vertexarray


def build(path):
    t=time.time()
    model=pymeshio.pmx.reader.read_from_file(path)
    if not model:
        return
    print(time.time()-t, "sec")
    # build
    basedir=os.path.dirname(path)
    indexedVertexArray=opengl.vertexarray.IndexedVertexArray()
    for v in model.vertices:
        # left-handed y-up to right-handed y-up                
        if v.deform.__class__ is pymeshio.pmx.Bdef1:
            indexedVertexArray.addVertex(
                    (v.position[0], v.position[1], -v.position[2], 1), 
                    (v.normal[0], v.normal[1], -v.normal[2]), 
                    (v.uv[0], v.uv[1]), 
                    (1, 1, 1, 1),
                    v.deform.index0, 0, 1.0)
        elif v.deform.__class__ is pymeshio.pmx.Bdef2:
            indexedVertexArray.addVertex(
                    (v.position[0], v.position[1], -v.position[2], 1), 
                    (v.normal[0], v.normal[1], -v.normal[2]), 
                    (v.uv[0], v.uv[1]), 
                    (1, 1, 1, 1),
                    v.deform.index0, v.deform.index1, v.deform.weight0)
        else:
            print("unknown deform: {0}".format(v.deform))
    
    # material
    textureMap={}
    faceIndex=0
    def indices():
        for i in model.indices:
            yield i
    indexGen=indices()
    for i, m in enumerate(model.materials):
        material=opengl.material.MQOMaterial()
        material.vcol=True
        material.rgba=(
                m.diffuse_color[0], 
                m.diffuse_color[1], 
                m.diffuse_color[2], 
                m.diffuse_alpha)
        if m.texture_index!=255:
            texturepath=os.path.join(basedir, model.textures[m.texture_index])
            if os.path.isfile(texturepath):
                if not texturepath in textureMap:
                    texture=opengl.texture.Texture(texturepath)
                    textureMap[texturepath]=texture
                material.texture=textureMap[texturepath]
        indices=indexedVertexArray.addMaterial(material)
        indices+=[next(indexGen) for n in range(m.vertex_count)]
    indexedVertexArray.optimize()
    return indexedVertexArray

