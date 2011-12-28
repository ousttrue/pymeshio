#!/usr/bin/env python
# coding: utf-8

import OpenGL.Tk


class Widget(OpenGL.Tk.RawOpengl):
    def __init__(self, master, engine, *args, **kw):
        #super(Widget, self).__init__(master, *args, **kw)
        OpenGL.Tk.RawOpengl.__init__(self, master, *args, **kw)
        self.engine=engine
        self.bind('<Map>', self.onDraw)
        self.bind('<Expose>', self.onDraw)
        self.bind('<Configure>', self.onResize)
        self.bind('<ButtonPress-1>', lambda e: self.engine.onLeftDown(e.x, e.y) and self.onDraw())
        self.bind('<ButtonRelease-1>', lambda e: self.engine.onLeftUp(e.x, e.y) and self.onDraw())
        self.bind('<B1-Motion>', lambda e: self.engine.onMotion(e.x, e.y) and self.onDraw())
        self.bind('<ButtonPress-2>', lambda e: self.engine.onMiddleDown(e.x, e.y) and self.onDraw())
        self.bind('<ButtonRelease-2>', lambda e: self.engine.onMiddleUp(e.x, e.y) and self.onDraw())
        self.bind('<B2-Motion>', lambda e: self.engine.onMotion(e.x, e.y) and self.onDraw())
        self.bind('<ButtonPress-3>', lambda e: self.engine.onRightDown(e.x, e.y) and self.onDraw())
        self.bind('<ButtonRelease-3>', lambda e: self.engine.onRightUp(e.x, e.y) and self.onDraw())
        self.bind('<B3-Motion>', lambda e: self.engine.onMotion(e.x, e.y) and self.onDraw())

    def onDraw(self, *dummy):
        self.tk.call(self._w, 'makecurrent')
        self.update_idletasks()
        self.engine.draw()
        self.tk.call(self._w, 'swapbuffers')

    def onResize(self, event):
        self.engine.onResize(event.width, event.height)
        self.onDraw()

