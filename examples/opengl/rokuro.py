#!/usr/bin/python
# coding: utf-8

import math
from OpenGL.GL import *
from OpenGL.GLU import *

from . import baseview

class RokuroView(baseview.BaseView):
    def __init__(self):
        super(RokuroView, self).__init__()
        self.w=1
        self.h=1
        self.head=0
        self.pitch=0
        self.SHIFT_FACTOR=0.001
        self.distance=100
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
        self.shiftX+=dx * self.distance * self.SHIFT_FACTOR
        self.shiftY+=dy * self.distance * self.SHIFT_FACTOR

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

    def look_bb(self, min_v, max_v):
        w=max_v[0]-min_v[0]
        h=max_v[1]-min_v[1]
        long_side=max(w, h)
        def deglee_to_radian(deglee):
            return math.pi*deglee/180.0
        d=long_side/math.tan(deglee_to_radian(30)) * 1.5
        self.distance=min_v[2]+d
        cx=min_v[0]+max_v[0]
        cy=min_v[1]+max_v[1]
        print(cx, cy)
        self.shiftX=-cx/2.0
        self.shiftY=-cy/2.0

