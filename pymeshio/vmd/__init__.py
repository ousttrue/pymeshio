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


class ShapeData(object):
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

class MotionData(object):
    """
    bone animation data.
    """
    __slots__=['name', 'frame', 'pos', 'q', 'complement']
    def __init__(self, name):
        self.name=name
        self.frame=-1
        self.pos=Vector3()
        self.q=Quaternion()

    def __cmp__(self, other):
        return cmp(self.frame, other.frame)

    def __str__(self):
        return '<MotionData "%s" %d %s%s>' % (self.name, self.frame, self.pos, self.q)

