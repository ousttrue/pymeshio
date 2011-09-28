#!/usr/bin/python
# coding: utf-8

from PIL import Image
from OpenGL.GL import *


class Texture(object):

    def __init__(self, path):
        self.path=path
        self.image=None

    def onInitialize(self):
        if not self.image:
            self.loadImage()

        assert(self.image)
        if self.createTexture():
            return True

    def loadImage(self):
        self.image=Image.open(self.path)
        if self.image:
            print("load image:", self.path)
            return True
        else:
            print("failt to load image:", self.path)
            return False

    def createTexture(self):
        self.texture=glGenTextures(1)
        if self.texture==0:
            print("fail to glGenTextures")
            return False

        channels=len(self.image.getbands())
        w, h=self.image.size
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        if channels==4:
            print("RGBA")
            glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 
                    0, GL_RGBA, GL_UNSIGNED_BYTE, self.image.tostring())
        elif channels==3:
            print("RGB")
            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 
                    0, GL_RGB, GL_UNSIGNED_BYTE, self.image.tostring())

    def begin(self):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def end(self):
        glDisable(GL_TEXTURE_2D)


