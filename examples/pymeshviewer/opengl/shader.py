#!/usr/bin/python
# coding: utf-8

from OpenGL.GL import *


# Checks for GL posted errors after appropriate calls
def printOpenGLError():
    err = glGetError()
    if (err != GL_NO_ERROR):
        print('GLERROR: ', gluErrorString(err))
        #sys.exit()


class Shader(object):

    def __init__(self, vs_src, fs_src):
        self.vs_src=vs_src
        self.fs_src=fs_src
        self.is_initialized=False

    def initialize(self):
        self.initShader(self.vs_src, self.fs_src)
        self.is_initialized=True

    def initShader(self, vertex_shader_source, fragment_shader_source):
        # create program
        self.program=glCreateProgram()
        print('create program')
        printOpenGLError()

        # vertex shader
        print('vertex shader')
        self.vs = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(self.vs, [vertex_shader_source])
        glCompileShader(self.vs)
        glAttachShader(self.program, self.vs)
        printOpenGLError()

        # fragment shader
        print('fragment shader')
        self.fs = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(self.fs, [fragment_shader_source])
        glCompileShader(self.fs)
        glAttachShader(self.program, self.fs)
        printOpenGLError()

        print('link...')
        glLinkProgram(self.program)
        printOpenGLError()

    def draw(self):
        if not self.is_initialized:
            self.initialize()

        if glUseProgram(self.program):
            printOpenGLError()

        pass
