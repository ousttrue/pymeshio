# coding: utf-8
import os
import sys
import struct
from .mmd import *

###############################################################################
# PMD
###############################################################################
def UshortVector():
    return []


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
            'ambient', 'vertex_count', '_texture', 'toon_index', 'flag',
            ]
    def getTexture(self): return from_str(self._texture)
    def setTexture(self, texture): self._texture=to_str(texture)
    texture=property(getTexture, setTexture)

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


# @return 各マテリアルについて、そのマテリアルが保持する面の回数だけ
# マテリアル自身を返す
def material_per_face(materials):
    for m in materials:
        for x in range(int(m.vertex_count/3)):
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
    __slots__=['_name', 'index', 'type', 'parent', 'ik', 'pos',
            'children', '_english_name', 'ik_index',
            'parent_index', 'tail_index', 'tail',
            ]
    def getName(self): return from_str(self._name)
    def setName(self, name): self._name=to_str(name)
    name=property(getName, setName)
    def getEnglishName(self): return from_str(self._english_name)
    def setEnglishName(self, english_name): self._english_name=to_str(english_name)
    english_name=property(getEnglishName, setEnglishName)

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
        for i in range(child_count):
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
    __slots__=['_name', 'type', 'indices', 'pos_list', '_english_name',
            'vertex_count']
    def getName(self): return from_str(self._name)
    def setName(self, name): self._name=to_str(name)
    name=property(getName, setName)
    def getEnglishName(self): return from_str(self._english_name)
    def setEnglishName(self, english_name): self._english_name=to_str(english_name)
    english_name=property(getEnglishName, setEnglishName)

    def __init__(self, name='skin'):
        self.name=name
        self.type=None
        self.indices=[]
        self.pos_list=[]
        self.english_name=''
        self.vertex_count=0

    def append(self, index, x, y, z):
        self.indices.append(index)
        self.pos_list.append(Vector3(x, y, z))

    def __str__(self):
        return '<Skin name: "%s", type: %d, vertex: %d>' % (
            self.name, self.type, len(self.indices))


class BoneGroup(object):
    __slots__=['_name', '_english_name']
    def getName(self): return from_str(self._name)
    def setName(self, name): self._name=to_str(name)
    name=property(getName, setName)
    def getEnglishName(self): return from_str(self._english_name)
    def setEnglishName(self, english_name): self._english_name=to_str(english_name)
    english_name=property(getEnglishName, setEnglishName)

    def __init__(self, name='group'): self._name=name; self._english_name='center'


SHAPE_SPHERE=0
SHAPE_BOX=1
SHAPE_CAPSULE=2

RIGIDBODY_KINEMATICS=0
RIGIDBODY_PHYSICS=1
RIGIDBODY_PHYSICS_WITH_BONE=2


class RigidBody(object):
    __slots__=['_name', 'boneIndex', 'group', 'target', 'shapeType',
            'w', 'h', 'd', 'position', 'rotation', 'weight',
            'linearDamping', 'angularDamping', 'restitution', 'friction', 'processType'
            ]
    def getName(self): return from_str(self._name)
    def setName(self, name): self._name=to_str(name)
    name=property(getName, setName)

    def __init__(self, name):
        self.name=name
        self.position=Vector3()
        self.rotation=Vector3()


class Constraint(object):
    __slots__=[ '_name', 'rigidA', 'rigidB', 'pos', 'rot',
            'constraintPosMin', 'constraintPosMax',
            'constraintRotMin', 'constraintRotMax',
            'springPos', 'springRot',
            ]
    def getName(self): return from_str(self._name)
    def setName(self, name): self._name=to_str(name)
    name=property(getName, setName)

    def __init__(self, name):
        self.name=name
        self.pos=Vector3()
        self.rot=Vector3()
        self.constraintPosMin=Vector3()
        self.constraintPosMax=Vector3()
        self.constraintRotMin=Vector3()
        self.constraintRotMax=Vector3()
        self.springPos=Vector3()
        self.springRot=Vector3()


class ToonTextures(object):
    __slots__=['_toon_textures']
    def __init__(self):
        self._toon_textures=[]
        for i in range(10):
            self._toon_textures.append('toon%02d.bmp' % (i+1))

    def __getitem__(self, key):
        return from_str(self._toon_textures[key])

    def __setitem__(self, key, value):
        self._toon_textures[key]=to_str(value)

    def __iter__(self):
        for toon_texture in self._toon_textures:
            yield from_str(toon_texture)


class IO(object):
    __slots__=['io', 'end', 'pos',
            'version', '_name', '_comment',
            '_english_name', '_english_comment',
            'vertices', 'indices', 'materials', 'bones', 
            'ik_list', 'morph_list',
            'face_list', 'bone_group_list', 'bone_display_list',
            'toon_textures',
            'no_parent_bones',
            'rigidbodies', 'constraints',
            ]
    def getName(self): return from_str(self._name)
    def setName(self, name): self._name=to_str(name)
    name=property(getName, setName)
    def getEnglishName(self): return from_str(self._english_name)
    def setEnglishName(self, english_name): self._english_name=to_str(english_name)
    english_name=property(getEnglishName, setEnglishName)
    def getComment(self): return from_str(self._comment)
    def setComment(self, comment): self._comment=to_str(comment)
    comment=property(getComment, setComment)
    def getEnglishComment(self): return from_str(self._english_comment)
    def setEnglishComment(self, english_comment): self._english_comment=to_str(english_comment)
    english_comment=property(getEnglishComment, setEnglishComment)

    def __init__(self):
        self.version=1.0
        self.name=''
        self.comment=''
        self.english_name=''
        self.english_comment=''
        self.vertices=[]
        self.indices=[]
        self.materials=[]
        self.bones=[]
        self.ik_list=[]
        self.morph_list=[]
        self.face_list=[]
        self.bone_group_list=[]
        self.bone_display_list=[]
        # extend
        self.toon_textures=ToonTextures()
        self.rigidbodies=[]
        self.constraints=[]
        # innner use
        self.no_parent_bones=[]

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
            self.version, self.name, len(self.vertices), len(self.indices),
            len(self.materials), len(self.bones), len(self.ik_list), len(self.morph_list))

    def _check_position(self):
        self.pos=self.io.tell()

    def read(self, path):
        size=os.path.getsize(path)
        with open(path, "rb") as f:
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
        io.write(struct.pack("20s", self.name))
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

        # skin disp list
        io.write(struct.pack("B", len(self.face_list)))
        for i in self.face_list:
            io.write(struct.pack("H", i))

        # bone disp list
        io.write(struct.pack("B", len(self.bone_group_list)))
        for g in self.bone_group_list:
            io.write(struct.pack("50s", g.name))

        io.write(struct.pack("I", len(self.bone_display_list)))
        for l in self.bone_display_list:
            io.write(struct.pack("=HB", *l))

        ############################################################
        # extend data
        ############################################################
        io.write(struct.pack("B", 1))
        # english name
        io.write(struct.pack("=20s", self.english_name))
        io.write(struct.pack("=256s", self.english_comment))
        # english bone name
        for bone in self.bones:
            io.write(struct.pack("=20s", bone.english_name))
        # english skin list
        for skin in self.morph_list:
            #print(skin.name)
            if skin.name==b'base':
                continue
            io.write(struct.pack("=20s", skin.english_name))
        # english bone list
        for bone_group in self.bone_group_list:
            io.write(struct.pack("50s", bone_group.english_name))
        # toon texture
        for toon_texture in self.toon_textures:
            io.write(struct.pack("=100s", toon_texture))
        # rigid
        io.write(struct.pack("I", len(self.rigidbodies)))
        for r in self.rigidbodies:
            io.write(struct.pack("=20sHBHB14fB",
                r.name, r.boneIndex, r.group, r.target, r.shapeType,
                r.w, r.h, r.d, 
                r.position.x, r.position.y, r.position.z, 
                r.rotation.x, r.rotation.y, r.rotation.z, 
                r.weight,
                r.linearDamping, r.angularDamping, r.restitution,
                r.friction, r.processType))

        # constraint
        io.write(struct.pack("I", len(self.constraints)))
        for c in self.constraints:
            io.write(struct.pack("=20sII24f",
                c.name, c.rigidA, c.rigidB,
                c.pos.x, c.pos.y, c.pos.z,
                c.rot.x, c.rot.y, c.rot.z,
                c.constraintPosMin.x, c.constraintPosMin.y, c.constraintPosMin.z,
                c.constraintPosMax.x, c.constraintPosMax.y, c.constraintPosMax.z,
                c.constraintRotMin.x, c.constraintRotMin.y, c.constraintRotMin.z,
                c.constraintRotMax.x, c.constraintRotMax.y, c.constraintRotMax.z,
                c.springPos.x, c.springPos.y, c.springPos.z,
                c.springRot.x, c.springRot.y, c.springRot.z
                ))

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
        if not self.loadPhysics():
            return False
        self._check_position()

        return True

    def _loadHeader(self):
        signature=struct.unpack("3s", self.io.read(3))[0]
        if signature!=b"Pmd":
            print("invalid signature", signature)
            return False
        self.version=struct.unpack("f", self.io.read(4))[0]
        self.name = truncate_zero(struct.unpack("20s", self.io.read(20))[0])
        self.comment = truncate_zero(
                struct.unpack("256s", self.io.read(256))[0])
        return True

    def _loadVertex(self):
        count = struct.unpack("I", self.io.read(4))[0]
        for i in range(count):
            self.vertices.append(Vertex(*struct.unpack("8f2H2B", self.io.read(38))))
        return True

    def _loadFace(self):
        count = struct.unpack("I", self.io.read(4))[0]
        for i in range(0, count, 3):
            self.indices+=struct.unpack("HHH", self.io.read(6))
        return True

    def _loadMaterial(self):
        count = struct.unpack("I", self.io.read(4))[0]
        for i in range(count):
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
        for i in range(size):
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
        for i in range(size):
            ik=IK(*struct.unpack("2H", self.io.read(4)))
            ik.length = struct.unpack("B", self.io.read(1))[0]
            ik.iterations = struct.unpack("H", self.io.read(2))[0]
            ik.weight = struct.unpack("f", self.io.read(4))[0]
            for j in range(ik.length):
                ik.children.append(struct.unpack("H", self.io.read(2))[0])
            self.ik_list.append(ik)
        return True

    def _loadSkin(self):
        size = struct.unpack("H", self.io.read(2))[0]
        for i in range(size):
            skin=Skin(truncate_zero(struct.unpack("20s", self.io.read(20))[0]))
            skin_size = struct.unpack("I", self.io.read(4))[0]
            skin.type = struct.unpack("B", self.io.read(1))[0]
            for j in range(skin_size):
                skin.indices.append(struct.unpack("I", self.io.read(4))[0])
                skin.pos_list.append(
                        Vector3(*struct.unpack("3f", self.io.read(12))))
            skin.english_name="skin%03d" % len(self.morph_list)
            self.morph_list.append(skin)
        return True

    def _loadSkinIndex(self):
        size = struct.unpack("B", self.io.read(1))[0]
        for i in range(size):
            self.face_list.append(struct.unpack("H", self.io.read(2))[0])
        return True

    def _loadBoneName(self):
        size = struct.unpack("B", self.io.read(1))[0]
        for i in range(size):
            self.bone_group_list.append(BoneGroup(
                truncate_zero(struct.unpack("50s", self.io.read(50))[0])))
        return True

    def _loadBoneIndex(self):
        size = struct.unpack("I", self.io.read(4))[0]
        for i in range(size):
            first=struct.unpack("H", self.io.read(2))[0]
            second=struct.unpack("B", self.io.read(1))[0]
            self.bone_display_list.append((first, second))
        return True

    def loadToonTexture(self):
        """
        100bytex10
        """
        for i in range(10):
            self.toon_textures[i]=truncate_zero(struct.unpack("100s", self.io.read(100))[0])
        return True

    def loadEnglishName(self):
        # english name
        self.english_name=truncate_zero(
                struct.unpack("20s", self.io.read(20))[0])
        self.english_comment=truncate_zero(
                struct.unpack("256s", self.io.read(256))[0])
        self._check_position()
        # english bone name
        for bone in self.bones:
            english_name=truncate_zero(
                    struct.unpack("20s", self.io.read(20))[0])
            bone.english_name=english_name
        self._check_position()
        # english skin list
        for skin in self.morph_list:
            if skin.name==b'base':
                continue
            english_name=truncate_zero(
                    struct.unpack("20s", self.io.read(20))[0])
            #skin=self.morph_list[index]
            if english_name!=skin.name:
                skin.english_name=english_name
        self._check_position()
        # english bone list
        for i in range(0, len(self.bone_group_list)):
            self.bone_group_list[i].english_name=truncate_zero(
                    struct.unpack("50s", self.io.read(50))[0])
        self._check_position()
        return True

    def loadPhysics(self):
        # 剛体リスト
        count = struct.unpack("I", self.io.read(4))[0]
        for i in range(count):
            name=truncate_zero(struct.unpack("20s", self.io.read(20))[0])
            rigidbody=RigidBody(name)
            rigidbody.boneIndex=struct.unpack("H", self.io.read(2))[0]
            rigidbody.group=struct.unpack("B", self.io.read(1))[0]
            rigidbody.target=struct.unpack("H", self.io.read(2))[0]
            rigidbody.shapeType=struct.unpack("B", self.io.read(1))[0]
            rigidbody.w=struct.unpack("f", self.io.read(4))[0]
            rigidbody.h=struct.unpack("f", self.io.read(4))[0]
            rigidbody.d=struct.unpack("f", self.io.read(4))[0]
            rigidbody.position.x=struct.unpack("f", self.io.read(4))[0]
            rigidbody.position.y=struct.unpack("f", self.io.read(4))[0]
            rigidbody.position.z=struct.unpack("f", self.io.read(4))[0]
            rigidbody.rotation.x=struct.unpack("f", self.io.read(4))[0]
            rigidbody.rotation.y=struct.unpack("f", self.io.read(4))[0]
            rigidbody.rotation.z=struct.unpack("f", self.io.read(4))[0]
            rigidbody.weight=struct.unpack("f", self.io.read(4))[0]
            rigidbody.linearDamping=struct.unpack("f", self.io.read(4))[0]
            rigidbody.angularDamping=struct.unpack("f", self.io.read(4))[0]
            rigidbody.restitution=struct.unpack("f", self.io.read(4))[0]
            rigidbody.friction=struct.unpack("f", self.io.read(4))[0]
            rigidbody.processType=struct.unpack("B", self.io.read(1))[0]
            self.rigidbodies.append(rigidbody)
        self._check_position()

        # ジョイントリスト
        count = struct.unpack("I", self.io.read(4))[0]
        for i in range(count):
            name=truncate_zero(struct.unpack("20s", self.io.read(20))[0])
            constraint=Constraint(name)
            constraint.rigidA=struct.unpack("I", self.io.read(4))[0]
            constraint.rigidB=struct.unpack("I", self.io.read(4))[0]
            constraint.pos.x=struct.unpack("f", self.io.read(4))[0]
            constraint.pos.y=struct.unpack("f", self.io.read(4))[0]
            constraint.pos.z=struct.unpack("f", self.io.read(4))[0]
            constraint.rot.x=struct.unpack("f", self.io.read(4))[0]
            constraint.rot.y=struct.unpack("f", self.io.read(4))[0]
            constraint.rot.z=struct.unpack("f", self.io.read(4))[0]
            constraint.constraintPosMin.x=struct.unpack("f", self.io.read(4))[0]
            constraint.constraintPosMin.y=struct.unpack("f", self.io.read(4))[0]
            constraint.constraintPosMin.z=struct.unpack("f", self.io.read(4))[0]
            constraint.constraintPosMax.x=struct.unpack("f", self.io.read(4))[0]
            constraint.constraintPosMax.y=struct.unpack("f", self.io.read(4))[0]
            constraint.constraintPosMax.z=struct.unpack("f", self.io.read(4))[0]
            constraint.constraintRotMin.x=struct.unpack("f", self.io.read(4))[0]
            constraint.constraintRotMin.y=struct.unpack("f", self.io.read(4))[0]
            constraint.constraintRotMin.z=struct.unpack("f", self.io.read(4))[0]
            constraint.constraintRotMax.x=struct.unpack("f", self.io.read(4))[0]
            constraint.constraintRotMax.y=struct.unpack("f", self.io.read(4))[0]
            constraint.constraintRotMax.z=struct.unpack("f", self.io.read(4))[0]
            constraint.springPos.x=struct.unpack("f", self.io.read(4))[0]
            constraint.springPos.y=struct.unpack("f", self.io.read(4))[0]
            constraint.springPos.z=struct.unpack("f", self.io.read(4))[0]
            constraint.springRot.x=struct.unpack("f", self.io.read(4))[0]
            constraint.springRot.y=struct.unpack("f", self.io.read(4))[0]
            constraint.springRot.z=struct.unpack("f", self.io.read(4))[0]
            self.constraints.append(constraint)
        self._check_position()

        return True

