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
# VMD
###############################################################################
class ShapeData(object):
    __slots__=['name', 'frame', 'ratio']
    def __init__(self, name):
        self.name=name
        self.frame=-1
        self.ratio=0

    def __cmp__(self, other):
        return cmp(self.frame, other.frame)

class MotionData(object):
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

class VMDLoader(object):
    __slots__=['io', 'end', 'signature',
            'model_name', 'last_frame',
            'motions', 'shapes', 'cameras', 'lights',
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

    def load(self, path, io, end):
        self.io=io
        self.end=end

        # signature
        self.signature=truncate_zero(self.io.read(30))
        version=self.validate_signature(self.signature)
        if not version:
            print("invalid signature", self.signature)
            return False

        if version==1:
            if not self.load_verstion_1():
                return False
        elif version==2:
            if not  self.load_verstion_2():
                return False 
        else:
            raise Exception("unknown version") 

        # post process
        motions=self.motions
        self.motions={}
        for m in motions:
            if not m.name in self.motions:
                self.motions[m.name]=[]
            self.motions[m.name].append(m)
        for name in self.motions.keys():
            self.motions[name].sort()

        shapes=self.shapes
        self.shapes={}
        for s in shapes:
            if not s.name in self.shapes:
                self.shapes[s.name]=[]
            self.shapes[s.name].append(s)
        for name in self.shapes.keys():
            self.shapes[name].sort()

        return True

    def getMotionCount(self):
        count=0
        for v in self.motions.values():
            count+=len(v)
        return count

    def getShapeCount(self):
        count=0
        for v in self.shapes.values():
            count+=len(v)
        return count

    def load_verstion_1(self):
        # model name
        self.model_name=truncate_zero(self.io.read(10))
        if not self.loadMotion_1():
            return False
        return True

    def loadMotion_1(self):
        count=struct.unpack('H', self.io.read(2))[0]
        self.io.read(2)
        for i in xrange(0, count):
            self.loadFrameData()
        return True

    ############################################################
    def load_verstion_2(self):
        # model name
        self.model_name=truncate_zero(self.io.read(20))

        if not self.loadMotion():
            return False
        if not self.loadShape():
            return False
        if not self.loadCamera():
            return False
        if not self.loadLight():
            return False
        #assert(self.io.tell()==self.end)
        #self.motions.sort(lambda l, r: l.name<r.name)

        return True

    def validate_signature(self, signature):
        if self.signature == "Vocaloid Motion Data 0002":
            return 2
        if self.signature == "Vocaloid Motion Data file":
            return 1
        else:
            return None

    def loadMotion(self):
        count=struct.unpack('I', self.io.read(4))[0]
        for i in xrange(0, count):
            self.loadFrameData()
        return True

    def loadShape(self):
        count=struct.unpack('I', self.io.read(4))[0]
        for i in xrange(0, count):
            self.loadShapeData()
        return True

    def loadCamera(self):
        count=struct.unpack('I', self.io.read(4))[0]
        for i in xrange(0, count):
            # not implemented
            assert(False)
            pass
        return True

    def loadLight(self):
        count=struct.unpack('I', self.io.read(4))[0]
        for i in xrange(0, count):
            # not implemented
            assert(False)
            pass
        return True

    def loadFrameData(self):
        """
        フレームひとつ分を読み込む
        """
        data=MotionData(truncate_zero(self.io.read(15)))
        (data.frame, data.pos.x, data.pos.y, data.pos.z,
        data.q.x, data.q.y, data.q.z, data.q.w) = struct.unpack(
                'I7f', self.io.read(32))
        # complement data
        data.complement=''.join(
                ['%x' % x for x in struct.unpack('64B', self.io.read(64))])
        self.motions.append(data)
        if data.frame>self.last_frame:
            self.last_frame=data.frame

    def loadShapeData(self):
        """
        モーフデータひとつ分を読み込む
        """
        data=ShapeData(truncate_zero(self.io.read(15)))
        (data.frame, data.ratio)=struct.unpack('If', self.io.read(8))
        self.shapes.append(data)
        if data.frame>self.last_frame:
            self.last_frame=data.frame

    # vmd -> csv
    ############################################################
    def create_csv_line(m):
        # quaternion -> euler angle
        (roll, pitch, yaw)=m.q.getRollPitchYaw()
        return '%s,%d,%g,%g,%g,%g,%g,%g,0x%s\n' % (
                m.name, m.frame, m.pos.x, m.pos.y, m.pos.z,
                to_degree(pitch), to_degree(yaw), to_degree(roll), m.complement
                )

    def write_csv(l, path):
        sys.setdefaultencoding('cp932')
        csv=open(path, "w")
        csv.write('%s,0\n' % l.signature)
        csv.write('%s\n' % l.model_name)
        # motion
        csv.write('%d\n' % len(l.motions))
        for m in l.motions:
            csv.write(create_csv_line(m))
        # shape
        csv.write('%d\n' % len(l.shapes))
        for s in l.shapes:
            csv.write('%s,%d,%f\n' % ( s.name, s.frame, s.ratio))
        # camera
        csv.write('%d\n' % len(l.cameras))
        for camera in l.cameras:
            assert(False)
        # light
        csv.write('%d\n' % len(l.lights))
        for light in l.lights:
            assert(False)


###############################################################################
# PMD
###############################################################################
class Vertex(object):
    __slots__=['pos', 'normal', 'uv', 'bone0', 'bone1', 'weight0', 'edge_flag']
    def __init__(self, x=0, y=0, z=0, nx=0, ny=0, nz=0, u=0, v=0,
            bone0=0, bone1=0, weight0=0, edge_flag=0):
        self.pos=Vector3(x, y, z)
        self.normal=Vector3(nx, ny, nz)
        self.uv=Vector2(u, v)
        self.bone0=bone0
        self.bone1=bone1
        self.weight0=weight0
        self.edge_flag=edge_flag

    def __str__(self):
        return "<%s %s %s, (%d, %d, %d)>" % (str(self.pos), str(self.normal), str(self.uv), self.bone0, self.bone1, self.weight0)

    def __getitem__(self, key):
        if key==0:
            return self.pos.x
        elif key==1:
            return self.pos.y
        elif key==2:
            return self.pos.z
        else:
            assert(False)

class Material(object):
    __slots__=[
            'diffuse', 'shinness', 'specular',
            'ambient', 'vertex_count', 'texture', 'toon_index', 'flag',
            ]

    def __init__(self, dr=0, dg=0, db=0, alpha=1, 
            specular=0, sr=0, sg=0, sb=0, ar=0, ag=0, ab=0):
        self.diffuse=RGBA(dr, dg, db, alpha)
        self.specular=RGBA(sr, sg, sb)
        self.shinness=specular
        self.ambient=RGBA(ar, ag, ab)
        self.vertex_count=0
        self.texture=''
        self.toon_index=0
        self.flag=0

    def __str__(self):
        return "<Material [%f, %f, %f, %f]>" % (
                self.diffuse[0], self.diffuse[1], 
                self.diffuse[2], self.diffuse[3],
                )

    def getTexture(self): return self.texture.decode('cp932')
    def setTexture(self, u): self.texture=u

# @return 各マテリアルについて、そのマテリアルが保持する面の回数だけ
# マテリアル自身を返す
def material_per_face(materials):
    for m in materials:
        for x in xrange(int(m.vertex_count/3)):
            yield m

class Bone(object):
    # kinds
    ROTATE = 0
    ROTATE_MOVE = 1
    IK = 2
    IK_ROTATE_INFL = 4
    ROTATE_INFL = 5
    IK_TARGET = 6
    UNVISIBLE = 7
    # since v4.0
    ROLLING=8 # ?
    TWEAK=9
    __slots__=['name', 'index', 'type', 'parent', 'ik', 'pos',
            'children', 'english_name', 'ik_index',
            'parent_index', 'tail_index', 'tail',
            ]
    def __init__(self, name='bone', type=0):
        self.name=name
        self.index=0
        self.type=type
        self.parent_index=0xFFFF
        self.tail_index=0
        self.tail=Vector3(0, 0, 0)
        self.parent=None
        self.ik_index=0xFFFF
        self.pos=Vector3(0, 0, 0)
        self.children=[]
        self.english_name=''

    def getName(self): return self.name.decode('cp932')
    def setName(self, u): self.name=u
    def setEnglishName(self, u): self.english_name=u

    def hasParent(self):
        return self.parent_index!=0xFFFF

    def hasChild(self):
        return self.tail_index!=0

    def display(self, indent=[]):
        if len(indent)>0:
            prefix=''
            for i, is_end in enumerate(indent):
                if i==len(indent)-1:
                    break
                else:
                    prefix+='  ' if is_end else ' |'
            uni='%s +%s(%s)' % (prefix, unicode(self), self.english_name)
            print(uni.encode(ENCODING))
        else:
            uni='%s(%s)' % (unicode(self), self.english_name)
            print(uni.encode(ENCODING))

        child_count=len(self.children)
        for i in xrange(child_count):
            child=self.children[i]
            if i<child_count-1:
                child.display(indent+[False])
            else:
                # last
                child.display(indent+[True])

# 0
class Bone_Rotate(Bone):
    __slots__=[]
    def __init__(self, name):
        super(Bone_Rotate, self).__init__(name, 0)
    def __str__(self):
        return '<ROTATE %s>' % (self.name)
# 1
class Bone_RotateMove(Bone):
    __slots__=[]
    def __init__(self, name):
        super(Bone_RotateMove, self).__init__(name, 1)
    def __str__(self):
        return '<ROTATE_MOVE %s>' % (self.name)
# 2
class Bone_IK(Bone):
    __slots__=[]
    def __init__(self, name):
        super(Bone_IK, self).__init__(name, 2)
    def __str__(self):
        return '<IK %s>' % (self.name)
# 4
class Bone_IKRotateInfl(Bone):
    __slots__=[]
    def __init__(self, name):
        super(Bone_IKRotateInfl, self).__init__(name, 4)
    def __str__(self):
        return '<IK_ROTATE_INFL %s>' % (self.name)
# 5
class Bone_RotateInfl(Bone):
    __slots__=[]
    def __init__(self, name):
        super(Bone_RotateInfl, self).__init__(name, 5)
    def __str__(self):
        return '<ROTATE_INFL %s>' % (self.name)
# 6
class Bone_IKTarget(Bone):
    __slots__=[]
    def __init__(self, name):
        super(Bone_IKTarget, self).__init__(name, 6)
    def __str__(self):
        return '<IK_TARGET %s>' % (self.name)
# 7
class Bone_Unvisible(Bone):
    __slots__=[]
    def __init__(self, name):
        super(Bone_Unvisible, self).__init__(name, 7)
    def __str__(self):
        return '<UNVISIBLE %s>' % (self.name)
# 8
class Bone_Rolling(Bone):
    __slots__=[]
    def __init__(self, name):
        super(Bone_Rolling, self).__init__(name, 8)
    def __str__(self):
        return '<ROLLING %s>' % (self.name)
# 9
class Bone_Tweak(Bone):
    __slots__=[]
    def __init__(self, name):
        super(Bone_Tweak, self).__init__(name, 9)
    def __str__(self):
        return '<TWEAK %s>' % (self.name)


def createBone(name, type):
    if type==0:
        return Bone_Rotate(name)
    elif type==1:
        return Bone_RotateMove(name)
    elif type==2:
        return Bone_IK(name)
    elif type==3:
        raise Exception("no used bone type: 3(%s)" % name)
    elif type==4:
        return Bone_IKRotateInfl(name)
    elif type==5:
        return Bone_RotateInfl(name)
    elif type==6:
        return Bone_IKTarget(name)
    elif type==7:
        return Bone_Unvisible(name)
    elif type==8:
        return Bone_Rolling(name)
    elif type==9:
        return Bone_Tweak(name)
    else:
        raise Exception("unknown bone type: %d(%s)", type, name)


class IK(object):
    __slots__=['index', 'target', 'iterations', 'weight', 'length', 'children']
    def __init__(self, index=0, target=0):
        self.index=index
        self.target=target
        self.iterations=None
        self.weight=None
        self.children=[]

    def __str__(self):
        return "<IK index: %d, target: %d, iterations: %d, weight: %f, children: %s(%d)>" %(self.index, self.target, self.iterations, self.weight, '-'.join([str(i) for i in self.children]), len(self.children))

class Skin(object):
    __slots__=['name', 'type', 'indices', 'pos_list', 'english_name',
            'vertex_count']
    def __init__(self, name='skin'):
        self.name=name
        self.type=None
        self.indices=[]
        self.pos_list=[]
        self.english_name=''
        self.vertex_count=0

    def getName(self): return self.name.decode('cp932')
    def setName(self, u): self.name=u
    def setEnglishName(self, u): self.english_name=u

    def append(self, index, x, y, z):
        self.indices.append(index)
        self.pos_list.append(Vector3(x, y, z))

    def __str__(self):
        return '<Skin name: "%s", type: %d, vertex: %d>' % (
            self.name, self.type, len(self.indices))

class ToonTexture(object):
    __slots__=['name']
    def __init__(self, name): self.name=name
    def getName(self): return self.name.decode('cp932')
    def setName(self, u): self.name=u

class BoneGroup(object):
    __slots__=['name', 'english_name']
    def __init__(self, name='group'): self.name=name; self.english_name='center'
    def getName(self): return self.name.decode('cp932')
    def setName(self, u): self.name=u
    def getEnglishName(self): return self.english_name.decode('cp932')
    def setEnglishName(self, u): self.english_name=u

class PMDLoader(object):
    __slots__=['io', 'end', 'pos',
            'version', 'model_name', 'comment',
            'english_model_name', 'english_comment',
            'vertices', 'indices', 'materials', 'bones', 
            'ik_list', 'morph_list',
            'face_list', 'bone_group_list', 'bone_display_list',
            'toon_textures',
            'no_parent_bones',
            'rigidbodies', 'constraints',
            ]
    def __init__(self):
        self.version=1.0
        self.model_name=b"default"
        self.comment=b"default"
        self.english_model_name=b'default'
        self.english_comment=b'default'
        self.vertices=[]
        self.indices=[]
        self.materials=[]
        self.bones=[]
        self.ik_list=[]
        self.morph_list=[]

        self.face_list=[]
        self.bone_group_list=[]
        self.bone_display_list=[]

        self.toon_textures=[
                ToonTexture(b'toon'), ToonTexture(b'toon'),
                ToonTexture(b'toon'), ToonTexture(b'toon'),
                ToonTexture(b'toon'), ToonTexture(b'toon'),
                ToonTexture(b'toon'), ToonTexture(b'toon'),
                ToonTexture(b'toon'), ToonTexture(b'toon'),
                ]

        self.no_parent_bones=[]

        self.rigidbodies=[]
        self.constraints=[]

    def getName(self): return self.model_name.decode('cp932')
    def setName(self, u): self.model_name=u
    def getComment(self): return self.comment.decode('cp932')
    def setComment(self, u): self.comment=u
    def getEnglishName(self): return self.english_model_name.decode('cp932')
    def setEnglishName(self, u): self.english_model_name=u
    def getEnglishComment(self): return self.english_comment.decode('cp932')
    def setEnglishComment(self, u): self.english_comment=u

    def getToonTexture(self, i): return self.toon_textures[i]
    def each_vertex(self): return self.vertices
    def getUV(self, i): return self.vertices[i].uv
    def addVertex(self): 
        v=Vertex()
        self.vertices.append(v)
        return v
    def addMaterial(self):
        m=Material()
        self.materials.append(m)
        return m
    def addBone(self):
        b=Bone()
        self.bones.append(b)
        return b
    def addIK(self):
        ik=IK()
        self.ik_list.append(ik)
        return ik
    def addMorph(self):
        s=Skin()
        self.morph_list.append(s)
        return s
    def addBoneGroup(self):
        g=BoneGroup()
        self.bone_group_list.append(g)
        return g
    def addBoneDisplay(self, b, g):
        self.bone_display_list.append((b, g))

    def __str__(self):
        return '<PMDLoader version: %g, model: "%s", vertex: %d, face: %d, material: %d, bone: %d ik: %d, skin: %d>' % (
            self.version, self.model_name, len(self.vertices), len(self.indices),
            len(self.materials), len(self.bones), len(self.ik_list), len(self.morph_list))

    def _check_position(self):
        """
        if self.pos:
            print(self.pos, self.io.tell()-self.pos)
        """
        self.pos=self.io.tell()
        pass

    def read(self, path):
        size=os.path.getsize(path)
        f=open(path, "rb")
        return self.load(path, f, size)

    def load(self, path, io, end):
        self.io=io
        self.pos=self.io.tell()
        self.end=end
        self._check_position()

        if not self._loadHeader():
            return False
        self._check_position()

        if not self._loadVertex():
            return False
        self._check_position()

        if not self._loadFace():
            return False
        self._check_position()

        if not self._loadMaterial():
            return False
        self._check_position()

        if not self._loadBone():
            return False
        self._check_position()

        if not self._loadIK():
            return False
        self._check_position()

        if not self._loadSkin():
            return False
        self._check_position()

        if not self._loadSkinIndex():
            return False
        self._check_position()

        if not self._loadBoneName():
            return False
        self._check_position()

        if not self._loadBoneIndex():
            return False
        self._check_position()

        if not self._loadExtend():
            print('fail to loadExtend')
            return False

        # 終端
        if self.io.tell()!=self.end:
            print("can not reach eof.")
            print("current: %d, end: %d, remain: %d" % (
                    self.io.tell(), self.end, self.end-self.io.tell()))

        # build bone tree
        for i, child in enumerate(self.bones):
            if child.parent_index==0xFFFF:
                # no parent
                self.no_parent_bones.append(child)
                child.parent=None
            else:
                # has parent
                parent=self.bones[child.parent_index]
                child.parent=parent
                parent.children.append(child)
            # 後位置
            if child.hasChild():
                child.tail=self.bones[child.tail_index].pos

        return True

    def write(self, path):
        io=open(path, 'wb')
        if not io:
            return False
        # Header
        io.write(b"Pmd")        
        io.write(struct.pack("f", self.version))
        io.write(struct.pack("20s", self.model_name))
        io.write(struct.pack("256s", self.comment))

        # Vertices
        io.write(struct.pack("I", len(self.vertices)))
        sVertex=struct.Struct("=8f2H2B") # 38byte
        assert(sVertex.size==38)
        for v in self.vertices:
            data=sVertex.pack( 
                v.pos[0], v.pos[1], v.pos[2],
                v.normal[0], v.normal[1], v.normal[2],
                v.uv[0], v.uv[1],
                v.bone0, v.bone1, v.weight0, v.edge_flag)
            io.write(data)

        # Faces
        io.write(struct.pack("I", len(self.indices)))
        io.write(struct.pack("=%dH" % len(self.indices), *self.indices))

        # material
        io.write(struct.pack("I", len(self.materials)))
        sMaterial=struct.Struct("=3fff3f3fBBI20s") # 70byte
        assert(sMaterial.size==70)
        for m in self.materials:
            io.write(sMaterial.pack(
                m.diffuse[0], m.diffuse[1], m.diffuse[2], m.diffuse[3],
                m.shinness, 
                m.specular[0], m.specular[1], m.specular[2],
                m.ambient[0], m.ambient[1], m.ambient[2],
                m.toon_index, m.flag,
                m.vertex_count,
                m.texture
                ))

        # bone
        io.write(struct.pack("H", len(self.bones)))
        sBone=struct.Struct("=20sHHBH3f")
        assert(sBone.size==39)
        for b in self.bones:
            io.write(sBone.pack(
                b.name,
                b.parent_index, b.tail_index, b.type, b.ik_index,
                b.pos[0], b.pos[1], b.pos[2]))

        # IK
        io.write(struct.pack("H", len(self.ik_list)))
        for ik in self.ik_list:
            io.write(struct.pack("=2HBHf", 
                ik.index, ik.target, ik.length, ik.iterations, ik.weight
                ))
            for c in ik.children:
                io.write(struct.pack("H", c))

        # skin
        io.write(struct.pack("H", len(self.morph_list)))
        for s in self.morph_list:
            io.write(struct.pack("20sIB", 
                s.name, len(s.indices), s.type))
            for i, v in zip(s.indices, s.pos_list):
                io.write(struct.pack("I3f", i, v[0], v[1], v[2]))

        # skin list
        io.write(struct.pack("B", len(self.face_list)))
        for i in self.face_list:
            io.write(struct.pack("H", i))

        # bone name
        io.write(struct.pack("B", len(self.bone_group_list)))
        for g in self.bone_group_list:
            io.write(struct.pack("50s", g.name))

        # bone list
        io.write(struct.pack("I", len(self.bone_display_list)))
        for l in self.bone_display_list:
            io.write(struct.pack("=HB", *l))

        # ToDo
        # Extend Data

        return True


    def _loadExtend(self):
        ############################################################
        # extend1: english name
        ############################################################
        if self.io.tell()>=self.end:
            return True
        if struct.unpack("B", self.io.read(1))[0]==1:
            if not self.loadEnglishName():
                return False
        self._check_position()

        ############################################################
        # extend2: toon texture list
        ############################################################
        if self.io.tell()>=self.end:
            return True
        if not self.loadToonTexture():
            return False
        self._check_position()

        ############################################################
        # extend3: physics
        ############################################################
        if self.io.tell()>=self.end:
            return True
        #if not self.loadPhysics():
        #    return False
        self._check_position()

        return True

    def _loadHeader(self):
        signature=struct.unpack("3s", self.io.read(3))[0]
        print(signature)
        if signature!=b"Pmd":
            print("invalid signature", signature)
            return False
        self.version=struct.unpack("f", self.io.read(4))[0]
        self.model_name = truncate_zero(struct.unpack("20s", self.io.read(20))[0])
        self.comment = truncate_zero(
                struct.unpack("256s", self.io.read(256))[0])
        return True

    def _loadVertex(self):
        count = struct.unpack("I", self.io.read(4))[0]
        for i in xrange(count):
            self.vertices.append(Vertex(*struct.unpack("8f2H2B", self.io.read(38))))
        return True

    def _loadFace(self):
        count = struct.unpack("I", self.io.read(4))[0]
        for i in xrange(0, count, 3):
            self.indices+=struct.unpack("HHH", self.io.read(6))
        return True

    def _loadMaterial(self):
        count = struct.unpack("I", self.io.read(4))[0]
        for i in xrange(count):
            material=Material(*struct.unpack("4ff3f3f", self.io.read(44)))
            material.toon_index=struct.unpack("B", self.io.read(1))[0]
            material.flag=struct.unpack("B", self.io.read(1))[0]
            material.vertex_count=struct.unpack("I", self.io.read(4))[0]
            texture=truncate_zero(struct.unpack("20s", self.io.read(20))[0])
            # todo sphere map
            #material.texture=texture.split('*')[0]
            material.texture=texture
            self.materials.append(material)
        return True

    def _loadBone(self):
        size = struct.unpack("H", self.io.read(2))[0]
        for i in xrange(size):
            name=truncate_zero(struct.unpack("20s", self.io.read(20))[0])
            parent_index, tail_index = struct.unpack("HH", self.io.read(4))
            type = struct.unpack("B", self.io.read(1))[0]
            bone=createBone(name, type)
            bone.parent_index=parent_index
            bone.tail_index=tail_index
            bone.ik_index = struct.unpack("H", self.io.read(2))[0]
            bone.pos = Vector3(*struct.unpack("3f", self.io.read(12)))
            bone.english_name="bone%03d" % len(self.bones)
            self.bones.append(bone)
        return True

    def _loadIK(self):
        size = struct.unpack("H", self.io.read(2))[0]
        for i in xrange(size):
            ik=IK(*struct.unpack("2H", self.io.read(4)))
            ik.length = struct.unpack("B", self.io.read(1))[0]
            ik.iterations = struct.unpack("H", self.io.read(2))[0]
            ik.weight = struct.unpack("f", self.io.read(4))[0]
            for j in xrange(ik.length):
                ik.children.append(struct.unpack("H", self.io.read(2))[0])
            self.ik_list.append(ik)
        return True

    def _loadSkin(self):
        size = struct.unpack("H", self.io.read(2))[0]
        for i in xrange(size):
            skin=Skin(truncate_zero(struct.unpack("20s", self.io.read(20))[0]))
            skin_size = struct.unpack("I", self.io.read(4))[0]
            skin.type = struct.unpack("B", self.io.read(1))[0]
            for j in xrange(skin_size):
                skin.indices.append(struct.unpack("I", self.io.read(4))[0])
                skin.pos_list.append(
                        Vector3(*struct.unpack("3f", self.io.read(12))))
            skin.english_name="skin%03d" % len(self.morph_list)
            self.morph_list.append(skin)
        return True

    def _loadSkinIndex(self):
        size = struct.unpack("B", self.io.read(1))[0]
        for i in xrange(size):
            self.face_list.append(struct.unpack("H", self.io.read(2))[0])
        return True

    def _loadBoneName(self):
        size = struct.unpack("B", self.io.read(1))[0]
        for i in xrange(size):
            self.bone_group_list.append(BoneGroup(
                truncate_zero(struct.unpack("50s", self.io.read(50))[0])))
        return True

    def _loadBoneIndex(self):
        size = struct.unpack("I", self.io.read(4))[0]
        for i in xrange(size):
            self.bone_display_list.append(struct.unpack("HB", self.io.read(3)))
        return True

    def loadToonTexture(self):
        """
        100bytex10
        """
        for i in xrange(10):
            self.toon_textures.append(ToonTexture(
                    truncate_zero(struct.unpack("100s", self.io.read(100))[0])))
        return True

    def loadEnglishName(self):
        # english name
        self.english_model_name=truncate_zero(
                struct.unpack("20s", self.io.read(20))[0])
        self.english_comment=truncate_zero(
                struct.unpack("256s", self.io.read(256))[0])
        # english bone list
        for bone in self.bones:
            english_name=truncate_zero(
                    struct.unpack("20s", self.io.read(20))[0])
            if english_name!=bone.name:
                bone.english_name=english_name
        # english skin list
        #for index in self.face_list:
        for skin in self.morph_list:
            if skin.name=='base':
                continue
            english_name=truncate_zero(
                    struct.unpack("20s", self.io.read(20))[0])
            #skin=self.morph_list[index]
            if english_name!=skin.name:
                skin.english_name=english_name
        # english bone list
        for i in xrange(0, len(self.bone_group_list)):
            self.bone_group_list[i].english_name=truncate_zero(
                    struct.unpack("50s", self.io.read(50))[0])
        return True

    def loadPhysics(self):
        # 剛体リスト
        count = struct.unpack("I", self.io.read(4))[0]
        for i in xrange(count):
            struct.unpack("83s", self.io.read(83))[0]
        # ジョイントリスト
        count = struct.unpack("I", self.io.read(4))[0]
        for i in xrange(count):
            struct.unpack("124s", self.io.read(124))[0]
        return True


###############################################################################
# VPD
###############################################################################
class LineLoader(object):
    """
    行指向の汎用ローダ
    """
    __slots__=['path', 'io', 'end']
    def __str__(self):
        return "<%s current:%d, end:%d>" % (
                self.__class__, self.getPos(), self.getEnd())

    def getPos(self):
        return self.io.tell()

    def getEnd(self):
        return self.end

    def readline(self):
        return (self.io.readline()).strip()

    def isEnd(self):
        return self.io.tell()>=self.end

    def load(self, path, io, end):
        self.path=path
        self.io=io
        self.end=end
        return self.process()

    def process(self):
        """
        dummy. read to end.
        """
        while not self.isEnd():
            self.io.readline()
        return True


class VPDLoader(LineLoader):
    __slots__=['pose']
    def __init__(self):
        super(VPDLoader, self).__init__()
        self.pose=[]

    def __str__(self):
        return "<VPD poses:%d>" % len(self.pose)

    def process(self):
        if self.readline()!="Vocaloid Pose Data file":
            return

        RE_OPEN=re.compile('^(\w+){(.*)')
        RE_OSM=re.compile('^\w+\.osm;')
        RE_COUNT=re.compile('^(\d+);')

        bone_count=-1
        while not self.isEnd():
            line=self.readline()
            if line=='':
                continue
            m=RE_OPEN.match(line)
            if m:
                if not self.parseBone(m.group(2)):
                    raise Exception("invalid bone")
                continue

            m=RE_OSM.match(line)
            if m:
                continue

            m=RE_COUNT.match(line)
            if m:
                bone_count=int(m.group(1))
                continue

        return len(self.pose)==bone_count

    def parseBone(self, name):
        bone=MotionData(name)
        self.pose.append(bone)
        bone.pos=Vector3(*[float(token) for token in self.readline().split(';')[0].split(',')])
        bone.q=Quaternion(*[float(token) for token in self.readline().split(';')[0].split(',')])
        return self.readline()=="}"


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

