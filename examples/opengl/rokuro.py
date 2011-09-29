#!/usr/bin/python
# coding: utf-8

from OpenGL.GL import *
from OpenGL.GLU import *

from . import baseview

class RokuroView(baseview.BaseView):
    def __init__(self, distance):
        super(RokuroView, self).__init__()
        self.w=1
        self.h=1
        self.head=0
        self.pitch=0
        self.distance=distance
        self.shiftX=0
        self.shiftY=0
        self.aspect=1
        self.n=1
        self.f=10000

    def onResize(self, w=None, h=None):
        super(RokuroView, self).onResize(w, h)
        self.aspect=float(self.w)/float(self.h)

    def dolly(self, d):
        if d>0:
            self.distance*=1.1
        elif d<0:
            self.distance*=0.9

    def shift(self, dx, dy):
        FACTOR=0.001
        self.shiftX+=dx * self.distance * FACTOR
        self.shiftY+=dy * self.distance * FACTOR

    def rotate(self, head, pitch):
        self.head+=head
        self.pitch+=pitch

    def updateProjection(self):
        gluPerspective(30, self.aspect, self.n, self.f)

    def updateView(self):
        glTranslate(self.shiftX, self.shiftY, -self.distance)
        glRotate(self.head, 0, 1, 0)
        glRotate(self.pitch, 1, 0, 0)

    def onMotion(self, x, y):
        redraw=False
        if self.isLeftDown:
            self.dolly(y-self.y)
            redraw=True
        if self.isMiddelDown:
            self.shift(x-self.x, self.y-y)
            redraw=True
        if self.isRightDown:
            self.rotate(x-self.x, y-self.y)
            redraw=True
        self.x=x
        self.y=y
        return redraw

    def onWheel(self, d):
        if d!=0:
            self.dolly(d)
            return True

