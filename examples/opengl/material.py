#!/usr/bin/pyhthon
# coding: utf-8

from OpenGL.GL import *
from . import texture

'''
Material

* 色
'''
class Material(object):
    def __init__(self, r, g, b, a):
        self.r=r
        self.g=g
        self.b=b
        self.a=a

    def begin(self):
        glColor4f(self.r, self.g, self.b, self.a)

    def end(self):
        pass

    def onInitialize(self):
        pass

    @staticmethod
    def create(src):
        m=material.Material(*src.col)
        return m


'''
Material

* 色
* テクスチャー
'''
class MQOMaterial(object):
    def __init__(self):
        self.rgba=(0, 0, 0, 0)
        self.vcol=False
        self.texture=None

    def __enter__(self):
        self.begin()

    def __exit__(self):
        self.end()

    def begin(self):
        glColor4f(*self.rgba)
        if self.texture:
            self.texture.begin()

        # backface culling
        glEnable(GL_CULL_FACE)
        glFrontFace(GL_CW)
        glCullFace(GL_BACK)
        # alpha test
        glEnable(GL_ALPHA_TEST);
        glAlphaFunc(GL_GREATER, 0.5);

    def end(self):
        if self.texture:
            self.texture.end()

    def onInitialize(self):
        pass
        #if self.texture:
        #    self.texture.onInitialize()

    @staticmethod
    def create(src, basedir):
        m=MQOMaterial(src.color)
        if src.tex:
            m.texture=texture.Texture((basedir+'/'+src.tex).replace('\\', '/'))
        return m

