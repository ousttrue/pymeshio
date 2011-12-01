# coding: utf-8
"""
VMDの読み込み
http://yumin3123.at.webry.info/200810/article_4.html
http://atupdate.web.fc2.com/vmd_format.htm
"""
__author__="ousttrue"
__license__="zlib"
__versioon__="1.0.0"


import io
import os
import struct
from .. import common


class MorphFrame(object):
    """
    morphing animation data.
    """
    __slots__=['name', 'frame', 'ratio']
    def __init__(self, name):
        self.name=name
        self.frame=-1
        self.ratio=0

    def __cmp__(self, other):
        return cmp(self.frame, other.frame)


class BoneFrame(object):
    """
    bone animation data.
    """
    __slots__=['name', 'frame', 'pos', 'q', 'complement']
    def __init__(self, name):
        self.name=name
        self.frame=-1
        self.pos=common.Vector3()
        self.q=common.Quaternion()

    def __cmp__(self, other):
        return cmp(self.frame, other.frame)

    def __str__(self):
        return '<BoneFrame "%s" %d %s%s>' % (self.name, self.frame, self.pos, self.q)


class Motion(object):
    __slots__=[
            'model_name',
            'motions',
            'shapes',
            'cameras',
            'lights',
            'last_frame',
            ]
    def __init__(self):
        self.model_name=''
        self.motions=[]
        self.shapes=[]
        self.cameras=[]
        self.lights=[]
        self.last_frame=0

    def __str__(self):
        return '<VMDLoader model: "%s", motion: %d, shape: %d, camera: %d, light: %d>' % (
            self.model_name, len(self.motions), len(self.shapes),
            len(self.cameras), len(self.lights))

