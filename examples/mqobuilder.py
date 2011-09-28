#!/usr/bin/env python
# coding: utf-8

import time
import os
import pymeshio.mqo
import material
import vertexarraymap


def build(path):
    # load scenee
    t=time.time()
    io=pymeshio.mqo.IO()
    if not io.read(path):
        return
    print(time.time()-t, "sec")
    # build
    basedir=os.path.dirname(path)
    vertexArrayMap=vertexarraymap.VertexArrayMapWithUV(
            [material.MQOMaterial.create(m, basedir) 
                for m in io.materials])
    for o in io.objects:
        # skip mikoto objects
        if o.name.startswith("anchor"):
            continue
        if o.name.startswith("bone:"):
            continue
        if o.name.startswith("MCS:"):
            continue

        for f in o.faces:
            if f.index_count==3:
                vertexArrayMap.addTriangle(
                        f.material_index,
                        o.vertices[f.indices[0]],
                        o.vertices[f.indices[1]],
                        o.vertices[f.indices[2]],
                        f.uv[0], f.uv[1], f.uv[2]
                        )
            elif f.index_count==4:
                # triangle 1
                vertexArrayMap.addTriangle(
                        f.material_index,
                        o.vertices[f.indices[0]],
                        o.vertices[f.indices[1]],
                        o.vertices[f.indices[2]],
                        f.uv[0], f.uv[1], f.uv[2]
                        )
                # triangle 2
                vertexArrayMap.addTriangle(
                        f.material_index,
                        o.vertices[f.indices[2]],
                        o.vertices[f.indices[3]],
                        o.vertices[f.indices[0]],
                        f.uv[2], f.uv[3], f.uv[0]
                        )

    vertexArrayMap.optimize()
    return vertexArrayMap

