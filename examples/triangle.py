# coding: utf-8
from OpenGL.GL import *


class Triangle(object):
    def __init__(self, size):
        self.size=size

    def draw(self):
        # 三角形描画開始
        glBegin(GL_TRIANGLES)
        # 左下
        glVertex(-self.size, -self.size)
        # 右下
        glVertex(self.size, -self.size)
        # 上
        glVertex(0, self.size)
        # 三角形描画終了
        glEnd()

