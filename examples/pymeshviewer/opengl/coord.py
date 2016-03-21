# coding: utf-8
from OpenGL.GL import *


class Coord(object):
    def __init__(self, size):
        self.size=size

    def draw(self):
        glBegin(GL_LINES)
        glColor(1, 0, 0); glVertex(0, 0, 0); glVertex(self.size, 0, 0)
        glColor(0.5, 0, 0); glVertex(0, 0, 0); glVertex(-self.size, 0, 0)
        glColor(0, 1, 0); glVertex(0, 0, 0); glVertex(0, self.size, 0)
        glColor(0, 0.5, 0); glVertex(0, 0, 0); glVertex(0, -self.size, 0)
        glColor(0, 0, 1); glVertex(0, 0, 0); glVertex(0, 0, self.size)
        glColor(0, 0, 0.5); glVertex(0, 0, 0); glVertex(0, 0, -self.size)
        glEnd()

