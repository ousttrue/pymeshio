#!/usr/bin/python
# coding: utf-8
"""
20091202: VPD読み込みを追加
20100318: PMD書き込みを追加
20100731: meshioと互換になるように改造

VMDの読み込み
http://yumin3123.at.webry.info/200810/article_4.html
http://atupdate.web.fc2.com/vmd_format.htm

PMDの読み込み
http://blog.goo.ne.jp/torisu_tetosuki/e/209ad341d3ece2b1b4df24abf619d6e4

VPDの読み込み

ToDo:
    rigdid bodies
    constraints
"""
import sys
import codecs
import os.path
import struct
import math
import re
#import numpy
from decimal import *

ENCODING='cp932'

if sys.version_info[0]>=3:
    xrange=range

###############################################################################
# utility
###############################################################################
if sys.version_info[0]<3:
    def truncate_zero(src):
        """
        0x00以降を捨てる
        """
        pos = src.find(b"\x00")
        assert(type(src)==bytes)
        if pos >= 0:
            return src[:pos]
        else:
            return src
else:
    def truncate_zero(src):
        """
        0x00以降を捨てる
        """
        pos = src.find(b"\x00")
        assert(type(src)==bytes)
        if pos >= 0:
            return src[:pos].decode('cp932')
        else:
            return src.decode('cp932')

def radian_to_degree(x):
    return x/math.pi * 180.0


###############################################################################
# geometry
###############################################################################
class Vector2(object):
    __slots__=['x', 'y']
    def __init__(self, x=0, y=0):
        self.x=x
        self.y=y

    def __str__(self):
        return "<%f %f>" % (self.x, self.y)

    def __getitem__(self, key):
        if key==0:
            return self.x
        elif key==1:
            return self.y
        else:
            assert(False)

    def to_tuple(self):
        return (self.x, self.y)


class Vector3(object):
    __slots__=['x', 'y', 'z']
    def __init__(self, x=0, y=0, z=0):
        self.x=x
        self.y=y
        self.z=z

    def __str__(self):
        return "<%f %f %f>" % (self.x, self.y, self.z)

    def __getitem__(self, key):
        if key==0:
            return self.x
        elif key==1:
            return self.y
        elif key==2:
            return self.z
        else:
            assert(False)

    def to_tuple(self):
        return (self.x, self.y, self.z)


class Quaternion(object):
    __slots__=['x', 'y', 'z', 'w']
    def __init__(self, x=0, y=0, z=0, w=1):
        self.x=x
        self.y=y
        self.z=z
        self.w=w

    def __str__(self):
        return "<%f %f %f %f>" % (self.x, self.y, self.z, self.w)

    def __mul__(self, rhs):
        u=numpy.array([self.x, self.y, self.z], 'f')
        v=numpy.array([rhs.x, rhs.y, rhs.z], 'f')
        xyz=self.w*v+rhs.w*u+numpy.cross(u, v)
        q=Quaternion(xyz[0], xyz[1], xyz[2], self.w*rhs.w-numpy.dot(u, v))
        return q

    def dot(self, rhs):
        return self.x*rhs.x+self.y*rhs.y+self.z*rhs.z+self.w*rhs.w

    def getMatrix(self):
        sqX=self.x*self.x
        sqY=self.y*self.y
        sqZ=self.z*self.z
        xy=self.x*self.y
        xz=self.x*self.z
        yz=self.y*self.z
        wx=self.w*self.x
        wy=self.w*self.y
        wz=self.w*self.z
        return numpy.array([
                # 1
                [1-2*sqY-2*sqZ, 2*xy+2*wz, 2*xz-2*wy, 0],
                # 2
                [2*xy-2*wz, 1-2*sqX-2*sqZ, 2*yz+2*wx, 0],
                # 3
                [2*xz+2*wy, 2*yz-2*wx, 1-2*sqX-2*sqY, 0],
                # 4
                [0, 0, 0, 1]],
                'f')

    def getRHMatrix(self):
        x=-self.x
        y=-self.y
        z=self.z
        w=self.w
        sqX=x*x
        sqY=y*y
        sqZ=z*z
        xy=x*y
        xz=x*z
        yz=y*z
        wx=w*x
        wy=w*y
        wz=w*z
        return numpy.array([
                # 1
                [1-2*sqY-2*sqZ, 2*xy+2*wz, 2*xz-2*wy, 0],
                # 2
                [2*xy-2*wz, 1-2*sqX-2*sqZ, 2*yz+2*wx, 0],
                # 3
                [2*xz+2*wy, 2*yz-2*wx, 1-2*sqX-2*sqY, 0],
                # 4
                [0, 0, 0, 1]],
                'f')

    def getRollPitchYaw(self):
        m=self.getMatrix()

        roll = math.atan2(m[0, 1], m[1, 1])
        pitch = math.asin(-m[2, 1])
        yaw = math.atan2(m[2, 0], m[2, 2])

        if math.fabs(math.cos(pitch)) < 1.0e-6:
            roll += m[0, 1] > math.pi if 0.0 else -math.pi
            yaw += m[2, 0] > math.pi if 0.0 else -math.pi

        return roll, pitch, yaw

    def getSqNorm(self):
        return self.x*self.x+self.y*self.y+self.z*self.z+self.w*self.w

    def getNormalized(self):
        f=1.0/self.getSqNorm()
        q=Quaternion(self.x*f, self.y*f, self.z*f, self.w*f)
        return q

    def getRightHanded(self):
        "swap y and z axis"
        return Quaternion(-self.x, -self.z, -self.y, self.w)

    @staticmethod
    def createFromAxisAngle(axis, rad):
        q=Quaternion()
        half_rad=rad/2.0
        c=math.cos(half_rad)
        s=math.sin(half_rad)
        return Quaternion(axis[0]*s, axis[1]*s, axis[2]*s, c)


class RGBA(object):
    __slots__=['r', 'g', 'b', 'a']
    def __init__(self, r=0, g=0, b=0, a=1):
        self.r=r
        self.g=g
        self.b=b
        self.a=a

    def __getitem__(self, key):
        if key==0:
            return self.r
        elif key==1:
            return self.g
        elif key==2:
            return self.b
        elif key==3:
            return self.a
        else:
            assert(False)




###############################################################################
# interface
###############################################################################
def load_pmd(path):
    size=os.path.getsize(path)
    f=open(path, "rb")
    l=PMDLoader()
    if l.load(path, f, size):
        return l

def load_vmd(path):
    size=os.path.getsize(path)
    f=open(path, "rb")
    l=VMDLoader()
    if l.load(path, f, size):
        return l

def load_vpd(path):
    f=open(path, 'rb')
    if not f:
        return;
    size=os.path.getsize(path)
    l=VPDLoader()
    if l.load(path, f, size):
        return l


###############################################################################
# debug
###############################################################################
def debug_pmd(path):
    l=load_pmd(path)
    if not l:
        print("fail to load")
        sys.exit()

    print(unicode(l).encode(ENCODING))
    print(l.comment.encode(ENCODING))
    print("<ボーン>".decode('utf-8').encode(ENCODING))
    for bone in l.no_parent_bones:
        print(bone.name.encode(ENCODING))
        bone.display()
    #for bone in l.bones:
    #    uni="%s:%s" % (bone.english_name, bone.name)
    #    print uni.encode(ENCODING)
    #for skin in l.morph_list:
    #    uni="%s:%s" % (skin.english_name, skin.name)
    #    print uni.encode(ENCODING)
    #for i, v in enumerate(l.vertices):
    #    print i, v
    #for i, f in enumerate(l.indices):
    #    print i, f
    for m in l.materials:
        print(m)

def debug_pmd_write(path, out):
    l=load_pmd(path)
    if not l:
        print("fail to load")
        sys.exit()

    if not l.write(out):
        print("fail to write")
        sys.exit()

def debug_vmd(path):
    l=load_vmd(path)
    if not l:
        print("fail to load")
        sys.exit()
    print(unicode(l).encode(ENCODING))

    #for m in l.motions[u'センター']:
    #    print m.frame, m.pos
    for n, m in l.shapes.items():
        print(unicode(n).encode(ENCODING), getEnglishSkinName(n))

def debug_vpd(path):
    l=load_vpd(path)
    if not l:
        print("fail to load")
        sys.exit()
    for bone in l.pose:
        print(unicode(bone).encode(ENCODING))

if __name__=="__main__":
    if len(sys.argv)<2:
        print("usage: %s {pmd file}" % sys.argv[0])
        print("usage: %s {vmd file}" % sys.argv[0])
        print("usage: %s {vpd file}" % sys.argv[0])
        print("usage: %s {pmd file} {export pmdfile}" % sys.argv[0])
        sys.exit()

    path=sys.argv[1]
    if not os.path.exists(path):
        print("no such file: %s" % path)

    if path.lower().endswith('.pmd'):
        if len(sys.argv)==2:
            debug_pmd(path)
        else:
            debug_pmd_write(path, sys.argv[2])
    elif path.lower().endswith('.vmd'):
        debug_vmd(path)
    elif path.lower().endswith('.vpd'):
        debug_vpd(path)
    else:
        print("unknown file type: %s" % path)
        sys.exit()

