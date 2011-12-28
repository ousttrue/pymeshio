#!/usr/bin/env python
# coding: utf-8

from OpenGL.GL import *

class BaseView(object):
    def __init__(self):
        self.x=0
        self.y=0
        self.w=1
        self.h=1
        self.isLeftDown=False
        self.isMiddelDown=False
        self.isRightDown=False

    def updateProjection(self):
        pass

    def updateView(self):
        pass

    def onResize(self, w=None, h=None):
        self.w=w or self.w
        self.h=h or self.h
        glViewport(0, 0, self.w, self.h)

    def onLeftDown(self, x, y):
        self.isLeftDown=True
        self.x=x
        self.y=y

    def onLeftUp(self, x, y):
        self.isLeftDown=False

    def onMiddleDown(self, x, y):
        self.isMiddelDown=True
        self.x=x
        self.y=y

    def onMiddleUp(self, x, y):
        self.isMiddelDown=False

    def onRightDown(self, x, y):
        self.isRightDown=True
        self.x=x
        self.y=y

    def onRightUp(self, x, y):
        self.isRightDown=False

    def onMotion(self, x, y):
        print("onMotion", x, y)

    def printMatrix(self, m):
        print(m[0][0], m[0][1], m[0][2], m[0][3])
        print(m[1][0], m[1][1], m[1][2], m[1][3])
        print(m[2][0], m[2][1], m[2][2], m[2][3])
        print(m[3][0], m[3][1], m[3][2], m[3][3])

