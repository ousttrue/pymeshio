#!/usr/bin/env python
# coding: utf-8

from OpenGL.GL import *
import re
from .baseview import *


DELEGATE_PATTERN=re.compile('^on[A-Z]')

class BaseController(object):
    def __init__(self, view):
        self.isInitialized=False
        self.setView(view)
        self.root=None

    def setRoot(self, root):
        self.root=root
        self.delegate(root)
        self.isInitialized=False

    def setView(self, view):
        self.view=view
        self.delegate(view)

    def delegate(self, to):
        for name in dir(to):  
            if DELEGATE_PATTERN.match(name):
                method = getattr(to, name)  
                setattr(self, name, method)

    def onUpdate(*args):pass
    def onLeftDown(*args):pass
    def onLeftUp(*args):pass
    def onMiddleDown(*args):pass
    def onMiddleUp(*args):pass
    def onRightDown(*args):pass
    def onRightUp(*args):pass
    def onMotion(*args):pass
    def onResize(*args):pass
    def onWheel(*args):pass
    def onKeyDown(*args):pass
    def onInitialize(*args):pass

    def initialize(self):
        self.view.onResize()
        glEnable(GL_DEPTH_TEST)
        # 初期化時の呼び出し
        self.onInitialize()

    def draw(self):
        if not self.isInitialized:
            self.initialize()
            self.isInitialized=True
        # OpenGLバッファのクリア
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # 投影行列のクリア
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self.view.updateProjection()
        # モデルビュー行列のクリア
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # OpenGL描画
        self.view.updateView()
        if self.root:
            self.root.draw()
        glFlush()

