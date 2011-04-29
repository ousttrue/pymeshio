#!BPY
# coding: utf-8
"""
 Name: 'MikuMikuDance model (.pmd)...'
 Blender: 248
 Group: 'Export'
 Tooltip: 'Export PMD file for MikuMikuDance.'
"""
__author__= ["ousttrue"]
__version__= "2.2"
__url__=()
__bpydoc__="""
pmd Importer

This script exports a pmd model.

0.1 20100318: first implementation.
0.2 20100519: refactoring. use C extension.
1.0 20100530: implement basic features.
1.1 20100612: integrate 2.4 and 2.5.
1.2 20100616: implement rigid body.
1.3 20100619: fix rigid body, bone weight.
1.4 20100626: refactoring.
1.5 20100629: sphere map.
1.6 20100710: toon texture & bone group.
1.7 20100711: separate vertex with normal or uv.
2.0 20100724: update for Blender2.53.
2.1 20100731: add full python module.
2.2 20101005: update for Blender2.54.
2.3 20101228: update for Blender2.55.
"""

bl_addon_info = {
        'category': 'Import/Export',
        'name': 'Export: MikuMikuDance Model Format (.pmd)',
        'author': 'ousttrue',
        'version': (2, 2),
        'blender': (2, 5, 3),
        'location': 'File > Export',
        'description': 'Export to the MikuMikuDance Model Format (.pmd)',
        'warning': '', # used for warning icon and text in addons panel
        'wiki_url': 'http://sourceforge.jp/projects/meshio/wiki/FrontPage',
        'tracker_url': 'http://sourceforge.jp/ticket/newticket.php?group_id=5081',
        }

MMD_SHAPE_GROUP_NAME='_MMD_SHAPE'
MMD_MB_NAME='mb_name'
MMD_MB_COMMENT='mb_comment'
MMD_COMMENT='comment'
BASE_SHAPE_NAME='Basis'
RIGID_NAME='rigid_name'
RIGID_SHAPE_TYPE='rigid_shape_type'
RIGID_PROCESS_TYPE='rigid_process_type'
RIGID_BONE_NAME='rigid_bone_name'
#RIGID_LOCATION='rigid_loation'
RIGID_GROUP='ribid_group'
RIGID_INTERSECTION_GROUP='rigid_intersection_group'
RIGID_WEIGHT='rigid_weight'
RIGID_LINEAR_DAMPING='rigid_linear_damping'
RIGID_ANGULAR_DAMPING='rigid_angular_damping'
RIGID_RESTITUTION='rigid_restitution'
RIGID_FRICTION='rigid_friction'
CONSTRAINT_NAME='constraint_name'
CONSTRAINT_A='const_a'
CONSTRAINT_B='const_b'
CONSTRAINT_POS_MIN='const_pos_min'
CONSTRAINT_POS_MAX='const_pos_max'
CONSTRAINT_ROT_MIN='const_rot_min'
CONSTRAINT_ROT_MAX='const_rot_max'
CONSTRAINT_SPRING_POS='const_spring_pos'
CONSTRAINT_SPRING_ROT='const_spring_rot'
TOON_TEXTURE_OBJECT='ToonTextures'


###############################################################################
# import
###############################################################################
import os
import sys

try:
    # C extension
    from meshio import pmd, englishmap
    print('use meshio C module')
except ImportError:
    # full python
    from pymeshio import englishmap
    from pymeshio import mmd as pmd
    pmd.IO=pmd.PMDLoader

def isBlender24():
    return sys.version_info[0]<3

if isBlender24():
    # for 2.4
    import Blender
    from Blender import Mathutils
    import bpy

    # wrapper
    import bl24 as bl

    def setMaterialParams(material, m):
        # diffuse
        material.diffuse.r=m.R
        material.diffuse.g=m.G
        material.diffuse.b=m.B
        material.diffuse.a=m.alpha
        # specular
        material.shinness=0 if m.spec<1e-5 else m.spec*10
        material.specular.r=m.specR
        material.specular.g=m.specG
        material.specular.b=m.specB
        # ambient
        material.ambient.r=m.mirR
        material.ambient.g=m.mirG
        material.ambient.b=m.mirB
        # flag
        material.flag=1 if m.enableSSS else 0

    def toCP932(s):
        return s


else:
    # for 2.5
    import bpy
    import mathutils

    # wrapper
    import bl25 as bl

    xrange=range

    def setMaterialParams(material, m):
        # diffuse
        material.diffuse.r=m.diffuse_color[0]
        material.diffuse.g=m.diffuse_color[1]
        material.diffuse.b=m.diffuse_color[2]
        material.diffuse.a=m.alpha
        # specular
        material.shinness=0 if m.specular_toon_size<1e-5 else m.specular_hardness*10
        material.specular.r=m.specular_color[0]
        material.specular.g=m.specular_color[1]
        material.specular.b=m.specular_color[2]
        # ambient
        material.ambient.r=m.mirror_color[0]
        material.ambient.g=m.mirror_color[1]
        material.ambient.b=m.mirror_color[2]
        # flag
        material.flag=1 if m.subsurface_scattering.enabled else 0
        # toon
        material.toon_index=7

    def toCP932(s):
        return s.encode('cp932')


class Node(object):
    __slots__=['o', 'children']
    def __init__(self, o):
        self.o=o
        self.children=[]


###############################################################################
# Blenderのメッシュをワンスキンメッシュ化する
###############################################################################
def near(x, y, EPSILON=1e-5):
    d=x-y
    return d>=-EPSILON and d<=EPSILON


class VertexAttribute(object):
    __slots__=[
            'nx', 'ny', 'nz', # normal
            'u', 'v', # uv
            ]
    def __init__(self, nx, ny, nz, u, v):
        self.nx=nx
        self.ny=ny
        self.nz=nz
        self.u=u
        self.v=v

    def __str__(self):
        return "<vkey: %f, %f, %f, %f, %f>" % (
                self.nx, self.ny, self.nz, self.u, self.v)

    def __hash__(self):
        return self.nx + self.ny + self.nz + self.u + self.v

    def __eq__(self, rhs):
        return self.nx==rhs.nx and self.ny==rhs.ny and self.nz==rhs.nz and self.u==rhs.u and self.v==rhs.v


class VertexKey(object):
    __slots__=[
            'obj_index', 'index',
            ]

    def __init__(self, obj_index, index):
        self.obj_index=obj_index
        self.index=index

    def __str__(self):
        return "<vkey: %d, %d>" % (self.obj_index, self.index)

    def __hash__(self):
        return self.index*100+self.obj_index

    def __eq__(self, rhs):
        return self.obj_index==rhs.obj_index and self.index==rhs.index


class VertexArray(object):
    """
    頂点配列
    """
    __slots__=[
            'indexArrays',
            'positions',
            'attributes', # normal and uv
            'b0', 'b1', 'weight',
            'vertexMap',
            'objectMap',
            ]
    def __init__(self):
        # indexArrays split with each material
        self.indexArrays={}

        self.positions=[]
        self.attributes=[]
        self.b0=[]
        self.b1=[]
        self.weight=[]

        self.vertexMap={}
        self.objectMap={}

    def __str__(self):
        return "<VertexArray %d positions, %d indexArrays>" % (
                len(self.positions), len(self.indexArrays))

    def zip(self):
        return zip(
                self.positions, self.attributes,
                self.b0, self.b1, self.weight)

    def each(self):
        keys=[key for key in self.indexArrays.keys()]
        keys.sort()
        for key in keys:
            yield(key, self.indexArrays[key])

    def __addOrGetIndex(self, obj_index, base_index, pos, normal, uv, b0, b1, weight0):
        key=VertexKey(obj_index, base_index)
        attribute=VertexAttribute( 
                normal[0], normal[1], normal[2],
                uv[0], uv[1])
        if key in self.vertexMap:
            if attribute in self.vertexMap[key]:
                return self.vertexMap[key][attribute]
            else:
                return self.__addVertex(self.vertexMap[key],
                        pos, attribute, b0, b1, weight0)
        else:
            vertexMapKey={}
            self.vertexMap[key]=vertexMapKey
            return self.__addVertex(vertexMapKey,
                    pos, attribute, b0, b1, weight0)

    def __addVertex(self, vertexMapKey, pos, attribute, b0, b1, weight0):
        index=len(self.positions)
        vertexMapKey[attribute]=index
        # position
        self.positions.append((pos.x, pos.y, pos.z))
        # unique attribute
        self.attributes.append(attribute)
        # shared attribute
        self.b0.append(b0)
        self.b1.append(b1)
        self.weight.append(weight0)
        assert(index<=65535)
        return index
            
    def getMappedIndex(self, obj_name, base_index):
        return self.vertexMap[VertexKey(self.objectMap[obj_name], base_index)]

    def addTriangle(self,
            object_name, material,
            base_index0, base_index1, base_index2,
            pos0, pos1, pos2,
            n0, n1, n2,
            uv0, uv1, uv2,
            b0_0, b0_1, b0_2,
            b1_0, b1_1, b1_2,
            weight0, weight1, weight2
            ):
        if object_name in self.objectMap:
            obj_index=self.objectMap[object_name]
        else:
            obj_index=len(self.objectMap)
            self.objectMap[object_name]=obj_index
        index0=self.__addOrGetIndex(obj_index, base_index0, pos0, n0, uv0, b0_0, b1_0, weight0)
        index1=self.__addOrGetIndex(obj_index, base_index1, pos1, n1, uv1, b0_1, b1_1, weight1)
        index2=self.__addOrGetIndex(obj_index, base_index2, pos2, n2, uv2, b0_2, b1_2, weight2)

        if not material in self.indexArrays:
            self.indexArrays[material]=[]
        self.indexArrays[material]+=[index0, index1, index2]


class Morph(object):
    __slots__=['name', 'type', 'offsets']
    def __init__(self, name, type):
        self.name=name
        self.type=type
        self.offsets=[]

    def add(self, index, offset):
        self.offsets.append((index, offset))

    def sort(self):
        if isBlender24():
            self.offsets.sort(lambda l, r: l[0]-r[0])
        else:
            self.offsets.sort(key=lambda e: e[0])

    def __str__(self):
        return "<Morph %s>" % self.name

class IKSolver(object):
    __slots__=['target', 'effector', 'length', 'iterations', 'weight']
    def __init__(self, target, effector, length, iterations, weight):
        self.target=target
        self.effector=effector
        self.length=length
        self.iterations=iterations
        self.weight=weight


class OneSkinMesh(object):
    __slots__=['vertexArray', 'morphList', 'rigidbodies', 'constraints', ]
    def __init__(self):
        self.vertexArray=VertexArray()
        self.morphList=[]
        self.rigidbodies=[]
        self.constraints=[]

    def __str__(self):
        return "<OneSkinMesh %s, morph:%d>" % (
                self.vertexArray,
                len(self.morphList))

    def addMesh(self, obj):
        if not bl.object.isVisible(obj):
            return
        self.__mesh(obj)
        self.__skin(obj)
        self.__rigidbody(obj)
        self.__constraint(obj)

    def __getWeightMap(self, obj, mesh):
        # bone weight
        weightMap={}
        secondWeightMap={}
        def setWeight(i, name, w):
            if w>0:
                if i in weightMap:
                    if i in secondWeightMap:
                        # 上位２つのweightを採用する
                        if w<secondWeightMap[i][1]:
                            pass
                        elif w<weightMap[i][1]:
                            # ２つ目を入れ替え
                            secondWeightMap[i]=(name, w)
                        else:
                            # １つ目を入れ替え
                            weightMap[i]=(name, w)
                    else:
                        if w>weightMap[i][1]:
                            # 多い方をweightMapに
                            secondWeightMap[i]=weightMap[i]
                            weightMap[i]=(name, w)
                        else:
                            secondWeightMap[i]=(name, w)
                else:
                    weightMap[i]=(name, w)

        # ToDo bone weightと関係ないvertex groupを除外する
        if isBlender24():
            for name in bl.object.getVertexGroupNames(obj):
                for i, w in mesh.getVertsFromGroup(name, 1):
                    setWeight(i, name, w)
        else:
            for i, v in enumerate(mesh.verts):
                if len(v.groups)>0:
                    for g in v.groups:
                        setWeight(i, obj.vertex_groups[g.group].name, g.weight)
                else:
                    setWeight(i, obj.vertex_groups[0].name, 1)

        # 合計値が1になるようにする
        for i in xrange(len(mesh.verts)):
            if i in secondWeightMap:
                secondWeightMap[i]=(secondWeightMap[i][0], 1.0-weightMap[i][1])
            elif i in weightMap:
                weightMap[i]=(weightMap[i][0], 1.0)
                secondWeightMap[i]=("", 0)
            else:
                print("no weight vertex")
                weightMap[i]=("", 0)
                secondWeightMap[i]=("", 0)

        return weightMap, secondWeightMap

    def __processFaces(self, obj_name, mesh, weightMap, secondWeightMap):
        # 各面の処理
        for i, face in enumerate(mesh.faces):
            faceVertexCount=bl.face.getVertexCount(face)
            material=mesh.materials[bl.face.getMaterialIndex(face)]
            v=[mesh.verts[index] for index in bl.face.getVertices(face)]
            uv=bl.mesh.getFaceUV(
                    mesh, i, face, bl.face.getVertexCount(face))
            # flip triangle
            if faceVertexCount==3:
                # triangle
                self.vertexArray.addTriangle(
                        obj_name, material.name,
                        v[2].index, 
                        v[1].index, 
                        v[0].index,
                        v[2].co, 
                        v[1].co, 
                        v[0].co,
                        bl.vertex.getNormal(v[2]), 
                        bl.vertex.getNormal(v[1]), 
                        bl.vertex.getNormal(v[0]),
                        uv[2], 
                        uv[1], 
                        uv[0],
                        weightMap[v[2].index][0],
                        weightMap[v[1].index][0],
                        weightMap[v[0].index][0],
                        secondWeightMap[v[2].index][0],
                        secondWeightMap[v[1].index][0],
                        secondWeightMap[v[0].index][0],
                        weightMap[v[2].index][1],
                        weightMap[v[1].index][1],
                        weightMap[v[0].index][1]
                        )
            elif faceVertexCount==4:
                # quadrangle
                self.vertexArray.addTriangle(
                        obj_name, material.name,
                        v[2].index, 
                        v[1].index, 
                        v[0].index,
                        v[2].co, 
                        v[1].co, 
                        v[0].co,
                        bl.vertex.getNormal(v[2]), 
                        bl.vertex.getNormal(v[1]), 
                        bl.vertex.getNormal(v[0]), 
                        uv[2], 
                        uv[1], 
                        uv[0],
                        weightMap[v[2].index][0],
                        weightMap[v[1].index][0],
                        weightMap[v[0].index][0],
                        secondWeightMap[v[2].index][0],
                        secondWeightMap[v[1].index][0],
                        secondWeightMap[v[0].index][0],
                        weightMap[v[2].index][1],
                        weightMap[v[1].index][1],
                        weightMap[v[0].index][1]
                        )
                self.vertexArray.addTriangle(
                        obj_name, material.name,
                        v[0].index, 
                        v[3].index, 
                        v[2].index,
                        v[0].co, 
                        v[3].co, 
                        v[2].co,
                        bl.vertex.getNormal(v[0]), 
                        bl.vertex.getNormal(v[3]), 
                        bl.vertex.getNormal(v[2]), 
                        uv[0], 
                        uv[3], 
                        uv[2],
                        weightMap[v[0].index][0],
                        weightMap[v[3].index][0],
                        weightMap[v[2].index][0],
                        secondWeightMap[v[0].index][0],
                        secondWeightMap[v[3].index][0],
                        secondWeightMap[v[2].index][0],
                        weightMap[v[0].index][1],
                        weightMap[v[3].index][1],
                        weightMap[v[2].index][1]
                        )

    def __mesh(self, obj):
        if isBlender24():
            pass
        else:
            if RIGID_SHAPE_TYPE in obj:
                return
            if CONSTRAINT_A in obj:
                return

        #if not bl.modifier.hasType(obj, 'ARMATURE'):
        #    return

        bl.message("export: %s" % obj.name)

        # メッシュのコピーを生成してオブジェクトの行列を適用する
        copyMesh, copyObj=bl.object.duplicate(obj)
        if len(copyMesh.verts)>0:
            # apply transform
            copyObj.scale=obj.scale
            bpy.ops.object.scale_apply()
            copyObj.rotation_euler=obj.rotation_euler
            bpy.ops.object.rotation_apply()
            copyObj.location=obj.location
            bpy.ops.object.location_apply()
            # apply modifier
            for m in [m for m in copyObj.modifiers]:
                if m.type=='SOLIDFY':
                    continue
                elif m.type=='ARMATURE':
                    continue
                elif m.type=='MIRROR':
                    bpy.ops.object.modifier_apply(modifier=m.name)
                else:
                    print(m.type)

            weightMap, secondWeightMap=self.__getWeightMap(copyObj, copyMesh)
            self.__processFaces(obj.name, copyMesh, weightMap, secondWeightMap)
        bl.object.delete(copyObj)

    def createEmptyBasicSkin(self):
        self.__getOrCreateMorph('base', 0)

    def __skin(self, obj):
        if not bl.object.hasShapeKey(obj):
            return

        indexRelativeMap={}
        blenderMesh=bl.object.getData(obj)
        baseMorph=None

        # shape keys
        vg=bl.object.getVertexGroup(obj, MMD_SHAPE_GROUP_NAME)

        # base
        used=set()
        for b in bl.object.getShapeKeys(obj):
            if b.name==BASE_SHAPE_NAME:
                baseMorph=self.__getOrCreateMorph('base', 0)
                basis=b

                relativeIndex=0
                for index in vg:
                    v=bl.shapekey.getByIndex(b, index)
                    pos=[v[0], v[1], v[2]]

                    indices=self.vertexArray.getMappedIndex(obj.name, index)
                    for attribute, i in indices.items():
                        if i in used:
                            continue
                        used.add(i)

                        baseMorph.add(i, pos)
                        indexRelativeMap[i]=relativeIndex
                        relativeIndex+=1

                break
        assert(basis)
        print(basis.name, len(baseMorph.offsets))

        if len(baseMorph.offsets)==0:
            return

        # shape keys
        for b in bl.object.getShapeKeys(obj):
            if b.name==BASE_SHAPE_NAME:
                continue

            print(b.name)
            morph=self.__getOrCreateMorph(b.name, 4)
            used=set()
            for index, src, dst in zip(
                    xrange(len(blenderMesh.verts)),
                    bl.shapekey.get(basis),
                    bl.shapekey.get(b)):
                offset=[dst[0]-src[0], dst[1]-src[1], dst[2]-src[2]]
                if offset[0]==0 and offset[1]==0 and offset[2]==0:
                    continue
                if index in vg:
                    indices=self.vertexArray.getMappedIndex(obj.name, index)
                    for attribute, i in indices.items():
                        if i in used:
                            continue
                        used.add(i) 
                        morph.add(indexRelativeMap[i], offset)
            assert(len(morph.offsets)<len(baseMorph.offsets))

        # sort skinmap
        original=self.morphList[:]
        def getIndex(morph):
            for i, v in enumerate(englishmap.skinMap):
                if v[0]==morph.name:
                    return i
            print(morph)
            return len(englishmap.skinMap)
        if isBlender24():
            self.morphList.sort(lambda l, r: getIndex(l)-getIndex(r))
        else:
            self.morphList.sort(key=getIndex)

    def __rigidbody(self, obj):
        if isBlender24():
            return
        if not RIGID_SHAPE_TYPE in obj:
            return
        self.rigidbodies.append(obj)

    def __constraint(self, obj):
        if isBlender24():
            return
        if not CONSTRAINT_A in obj:
            return
        self.constraints.append(obj)

    def __getOrCreateMorph(self, name, type):
        for m in self.morphList:
            if m.name==name:
                return m
        m=Morph(name, type)
        self.morphList.append(m)
        return m

    def getVertexCount(self):
        return len(self.vertexArray.positions)


class Bone(object):
    __slots__=['index', 'name', 'ik_index',
            'pos', 'tail', 'parent_index', 'tail_index', 'type', 'isConnect']
    def __init__(self, name, pos, tail, isConnect):
        self.index=-1
        self.name=name
        self.pos=pos
        self.tail=tail
        self.parent_index=None
        self.tail_index=None
        self.type=0
        self.isConnect=isConnect
        self.ik_index=0

    def __eq__(self, rhs):
        return self.index==rhs.index

    def __str__(self):
        return "<Bone %s %d>" % (self.name, self.type)

class BoneBuilder(object):
    __slots__=['bones', 'boneMap', 'ik_list', 'bone_groups',]
    def __init__(self):
        self.bones=[]
        self.boneMap={}
        self.ik_list=[]
        self.bone_groups=[]

    def getBoneGroup(self, bone):
        for i, g in enumerate(self.bone_groups):
            for b in g[1]:
                if b==bone.name:
                    return i+1
        print('no gorup', bone)
        return 0

    def build(self, armatureObj):
        if not armatureObj:
            return

        bl.message("build skeleton")
        armature=bl.object.getData(armatureObj)

        ####################
        # bone group
        ####################
        for g in bl.object.boneGroups(armatureObj):
            self.bone_groups.append((g.name, []))

        ####################
        # get bones
        ####################
        for b in armature.bones.values():
            if not b.parent:
                # root bone
                bone=Bone(b.name, 
                        bl.bone.getHeadLocal(b),
                        bl.bone.getTailLocal(b),
                        False)
                self.__addBone(bone)
                self.__getBone(bone, b)

        for b in armature.bones.values():
            if not b.parent:
                self.__checkConnection(b, None)

        ####################
        # get IK
        ####################
        pose = bl.object.getPose(armatureObj)
        for b in pose.bones.values():
            ####################
            # assing bone group
            ####################
            self.__assignBoneGroup(b, b.bone_group)
            for c in b.constraints:
                if bl.constraint.isIKSolver(c):
                    ####################
                    # IK target
                    ####################
                    target=self.__boneByName(bl.constraint.ikTarget(c))
                    target.type=2

                    ####################
                    # IK effector
                    ####################
                    # IK 接続先
                    link=self.__boneByName(b.name)
                    link.type=6

                    # IK chain
                    e=b.parent
                    chainLength=bl.constraint.ikChainLen(c)
                    for i in range(chainLength):
                        # IK影響下
                        chainBone=self.__boneByName(e.name)
                        chainBone.type=4
                        chainBone.ik_index=target.index
                        e=e.parent
                    self.ik_list.append(
                            IKSolver(target, link, chainLength, 
                                int(bl.constraint.ikItration(c) * 0.1), 
                                bl.constraint.ikRotationWeight(c)
                                ))

        ####################

        # boneのsort
        self._sortBy()
        self._fix()
        # IKのsort
        def getIndex(ik):
            for i, v in enumerate(englishmap.boneMap):
                if v[0]==ik.target.name:
                    return i
            return len(englishmap.boneMap)
        if isBlender24():
            self.ik_list.sort(lambda l, r: getIndex(l)-getIndex(r))
        else:
            self.ik_list.sort(key=getIndex)

    def __assignBoneGroup(self, poseBone, boneGroup):
        if boneGroup:
            for g in self.bone_groups:
                if g[0]==boneGroup.name:
                    g[1].append(poseBone.name)

    def __checkConnection(self, b, p):
        if bl.bone.isConnected(b):
            parent=self.__boneByName(p.name)
            parent.isConnect=True

        for c in b.children:
            self.__checkConnection(c, b)

    def _sortBy(self):
        """
        boneMap順に並べ替える
        """
        boneMap=englishmap.boneMap
        original=self.bones[:]
        def getIndex(bone):
            for i, k_v in enumerate(boneMap):
                if k_v[0]==bone.name:
                    return i
            print(bone)
            return len(boneMap)

        if isBlender24():
            self.bones.sort(lambda l, r: getIndex(l)-getIndex(r))
        else:
            self.bones.sort(key=getIndex)

        sortMap={}
        for i, b in enumerate(self.bones):
            src=original.index(b)
            sortMap[src]=i
        for b in self.bones:
            b.index=sortMap[b.index]
            if b.parent_index:
                b.parent_index=sortMap[b.parent_index]
            if b.tail_index:
                b.tail_index=sortMap[b.tail_index]
            if b.ik_index>0:
                b.ik_index=sortMap[b.ik_index]

    def _fix(self):
        """
        調整
        """
        for b in self.bones:
            # parent index
            if b.parent_index==None:
                b.parent_index=0xFFFF
            else:
                if b.type==6 or b.type==7:
                    # fix tail bone
                    parent=self.bones[b.parent_index]
                    #print('parnet', parent.name)
                    parent.tail_index=b.index

        for b in self.bones:
            if b.tail_index==None:
                b.tail_index=0
            elif b.type==9:
                b.tail_index==0

    def getIndex(self, bone):
        for i, b in enumerate(self.bones):
            if b==bone:
                return i
        assert(false)

    def indexByName(self, name):
        if name=='':
            return 0
        else:
            return self.getIndex(self.__boneByName(name))

    def __boneByName(self, name):
        return self.boneMap[name]
                    
    def __getBone(self, parent, b):
        if len(b.children)==0:
            parent.type=7
            return

        for i, c in enumerate(b.children):
            bone=Bone(c.name, 
                    bl.bone.getHeadLocal(c),
                    bl.bone.getTailLocal(c),
                    bl.bone.isConnected(c))
            self.__addBone(bone)
            if parent:
                bone.parent_index=parent.index
                #if i==0:
                if bone.isConnect or (not parent.tail_index and parent.tail==bone.pos):
                    parent.tail_index=bone.index
            self.__getBone(bone, c)

    def __addBone(self, bone):
        bone.index=len(self.bones)
        self.bones.append(bone)
        self.boneMap[bone.name]=bone


class PmdExporter(object):

    __slots__=[
            'armatureObj',
            'oneSkinMesh',
            'englishName',
            'englishComment',
            'name',
            'comment',
            'skeleton',
            ]
    def setup(self):
        self.armatureObj=None

        # 木構造を構築する
        object_node_map={}
        for o in bl.object.each():
            object_node_map[o]=Node(o)
        for o in bl.object.each():
            node=object_node_map[o]
            if node.o.parent:
                object_node_map[node.o.parent].children.append(node)

        # ルートを得る
        root=object_node_map[bl.object.getActive()]
        o=root.o
        self.englishName=o.name
        self.englishComment=o[MMD_COMMENT] if MMD_COMMENT in o else 'blender export\n'
        self.name=o[MMD_MB_NAME] if MMD_MB_NAME in o else 'Blenderエクスポート'
        self.comment=o[MMD_MB_COMMENT] if MMD_MB_COMMENT in o else 'Blnderエクスポート\n'

        # ワンスキンメッシュを作る
        self.oneSkinMesh=OneSkinMesh()
        self.__createOneSkinMesh(root)
        bl.message(self.oneSkinMesh)
        if len(self.oneSkinMesh.morphList)==0:
            # create emtpy skin
            self.oneSkinMesh.createEmptyBasicSkin()

        # skeleton
        self.skeleton=BoneBuilder()
        self.skeleton.build(self.armatureObj)

    def __createOneSkinMesh(self, node):
        ############################################################
        # search armature modifier
        ############################################################
        for m in node.o.modifiers:
            if bl.modifier.isType(m, 'ARMATURE'):
                armatureObj=bl.modifier.getArmatureObject(m)
                if not self.armatureObj:
                    self.armatureObj=armatureObj
                elif self.armatureObj!=armatureObj:
                    print("warning! found multiple armature. ignored.", 
                            armatureObj.name)

        if node.o.type.upper()=='MESH':
            self.oneSkinMesh.addMesh(node.o)

        for child in node.children:
            self.__createOneSkinMesh(child)

    def write(self, path):
        io=pmd.IO()
        io.setName(toCP932(self.name))
        io.setComment(toCP932(self.comment))
        io.version=1.0

        # 頂点
        for pos, attribute, b0, b1, weight in self.oneSkinMesh.vertexArray.zip():
            # convert right-handed z-up to left-handed y-up
            v=io.addVertex()
            v.pos.x=pos[0]
            v.pos.y=pos[2]
            v.pos.z=pos[1]
            v.normal.x=attribute.nx
            v.normal.y=attribute.ny
            v.normal.z=attribute.nz
            v.uv.x=attribute.u
            v.uv.y=1.0-attribute.v # reverse vertical
            v.bone0=self.skeleton.indexByName(b0)
            v.bone1=self.skeleton.indexByName(b1)
            v.weight0=int(100*weight)
            v.edge_flag=0 # edge flag, 0: enable edge, 1: not edge

        # 面とマテリアル
        vertexCount=self.oneSkinMesh.getVertexCount()
        for material_name, indices in self.oneSkinMesh.vertexArray.each():
            #print('material:', material_name)
            m=bl.material.get(material_name)
            # マテリアル
            material=io.addMaterial()
            setMaterialParams(material, m)

            material.vertex_count=len(indices)
            material.toon_index=0
            textures=[os.path.basename(path) 
                for path in bl.material.eachEnalbeTexturePath(m)]
            if len(textures)>0:
                material.setTexture(toCP932('*'.join(textures)))
            else:
                material.setTexture(toCP932(""))
            # 面
            for i in indices:
                assert(i<vertexCount)
            for i in xrange(0, len(indices), 3):
                # reverse triangle
                io.indices.append(indices[i])
                io.indices.append(indices[i+1])
                io.indices.append(indices[i+2])

        # bones
        boneNameMap={}
        for i, b in enumerate(self.skeleton.bones):
            bone=io.addBone()

            # name
            boneNameMap[b.name]=i
            v=englishmap.getUnicodeBoneName(b.name)
            if not v:
                v=[b.name, b.name]
            assert(v)
            cp932=v[1].encode('cp932')
            assert(len(cp932)<20)
            bone.setName(cp932)

            # english name
            bone_english_name=toCP932(b.name)
            assert(len(bone_english_name)<20)
            bone.setEnglishName(bone_english_name)

            if len(v)>=3:
                # has type
                if v[2]==5:
                    b.ik_index=self.skeleton.indexByName('eyes')
                bone.type=v[2]
            else:
                bone.type=b.type

            bone.parent_index=b.parent_index
            bone.tail_index=b.tail_index
            bone.ik_index=b.ik_index

            # convert right-handed z-up to left-handed y-up
            bone.pos.x=b.pos[0] if not near(b.pos[0], 0) else 0
            bone.pos.y=b.pos[2] if not near(b.pos[2], 0) else 0
            bone.pos.z=b.pos[1] if not near(b.pos[1], 0) else 0

        # IK
        for ik in self.skeleton.ik_list:
            solver=io.addIK()
            solver.index=self.skeleton.getIndex(ik.target)
            solver.target=self.skeleton.getIndex(ik.effector)
            solver.length=ik.length
            b=self.skeleton.bones[ik.effector.parent_index]
            for i in xrange(solver.length):
                solver.children.append(self.skeleton.getIndex(b))
                b=self.skeleton.bones[b.parent_index]
            solver.iterations=ik.iterations
            solver.weight=ik.weight

        # 表情
        for i, m in enumerate(self.oneSkinMesh.morphList):
            # morph
            morph=io.addMorph()

            v=englishmap.getUnicodeSkinName(m.name)
            if not v:
                v=[m.name, m.name, 0]
            assert(v)
            cp932=v[1].encode('cp932')
            morph.setName(cp932)
            morph.setEnglishName(m.name.encode('cp932'))
            m.type=v[2]
            morph.type=v[2]
            for index, offset in m.offsets:
                # convert right-handed z-up to left-handed y-up
                morph.append(index, offset[0], offset[2], offset[1])
            morph.vertex_count=len(m.offsets)

        # 表情枠
        # type==0はbase
        for i, m in enumerate(self.oneSkinMesh.morphList):
            if m.type==3:
                io.face_list.append(i)
        for i, m in enumerate(self.oneSkinMesh.morphList):
            if m.type==2:
                io.face_list.append(i)
        for i, m in enumerate(self.oneSkinMesh.morphList):
            if m.type==1:
                io.face_list.append(i)
        for i, m in enumerate(self.oneSkinMesh.morphList):
            if m.type==4:
                io.face_list.append(i)

        # ボーングループ
        for g in self.skeleton.bone_groups:
            boneDisplayName=io.addBoneGroup()
            # name
            name=englishmap.getUnicodeBoneGroupName(g[0])
            if not name:
                name=g[0]
            boneDisplayName.setName(toCP932(name+'\n'))
            # english
            englishName=g[0]
            boneDisplayName.setEnglishName(toCP932(englishName+'\n'))

        # ボーングループメンバー
        for i, b in enumerate(self.skeleton.bones):
            if i==0:
               continue
            if b.type in [6, 7]:
               continue
            io.addBoneDisplay(i, self.skeleton.getBoneGroup(b))

        #assert(len(io.bones)==len(io.bone_display_list)+1)

        # English
        io.setEnglishName(toCP932(self.englishName))
        io.setEnglishComment(toCP932(self.englishComment))

        # toon
        toonMeshObject=None
        for o in bl.object.each():
            try:
                if o.name.startswith(TOON_TEXTURE_OBJECT):
                    toonMeshObject=o
            except:
                p(o.name)
            break
        if toonMeshObject:
            toonMesh=bl.object.getData(toonMeshObject)
            toonMaterial=bl.mesh.getMaterial(toonMesh, 0)
            for i in range(10):
                t=bl.material.getTexture(toonMaterial, i)
                if t:
                    io.getToonTexture(i).setName(toCP932(t.name))
                else:
                    io.getToonTexture(i).setName(toCP932("toon%02d.bmp\n" % i))
        else:
            for i in range(10):
                io.getToonTexture(i).setName(toCP932("toon%02d.bmp\n" % i))

        # rigid body
        rigidNameMap={}
        for i, obj in enumerate(self.oneSkinMesh.rigidbodies):
            name=obj[RIGID_NAME] if RIGID_NAME in obj else obj.name
            print(name)
            rigidBody=io.addRigidBody()
            rigidBody.setName(name.encode('cp932'))
            rigidNameMap[name]=i
            boneIndex=boneNameMap[obj[RIGID_BONE_NAME]]
            if boneIndex==0:
                boneIndex=0xFFFF
                bone=self.skeleton.bones[0]
            else:
                bone=self.skeleton.bones[boneIndex]
            rigidBody.boneIndex=boneIndex
            #rigidBody.position.x=obj[RIGID_LOCATION][0]
            #rigidBody.position.y=obj[RIGID_LOCATION][1]
            #rigidBody.position.z=obj[RIGID_LOCATION][2]
            rigidBody.position.x=obj.location.x-bone.pos[0]
            rigidBody.position.y=obj.location.z-bone.pos[2]
            rigidBody.position.z=obj.location.y-bone.pos[1]
            rigidBody.rotation.x=-obj.rotation_euler[0]
            rigidBody.rotation.y=-obj.rotation_euler[2]
            rigidBody.rotation.z=-obj.rotation_euler[1]
            rigidBody.processType=obj[RIGID_PROCESS_TYPE]
            rigidBody.group=obj[RIGID_GROUP]
            rigidBody.target=obj[RIGID_INTERSECTION_GROUP]
            rigidBody.weight=obj[RIGID_WEIGHT]
            rigidBody.linearDamping=obj[RIGID_LINEAR_DAMPING]
            rigidBody.angularDamping=obj[RIGID_ANGULAR_DAMPING]
            rigidBody.restitution=obj[RIGID_RESTITUTION]
            rigidBody.friction=obj[RIGID_FRICTION]
            if obj[RIGID_SHAPE_TYPE]==0:
                rigidBody.shapeType=pmd.SHAPE_SPHERE
                rigidBody.w=obj.scale[0]
            elif obj[RIGID_SHAPE_TYPE]==1:
                rigidBody.shapeType=pmd.SHAPE_BOX
                rigidBody.w=obj.scale[0]
                rigidBody.d=obj.scale[1]
                rigidBody.h=obj.scale[2]
            elif obj[RIGID_SHAPE_TYPE]==2:
                rigidBody.shapeType=pmd.SHAPE_CAPSULE
                rigidBody.w=obj.scale[0]
                rigidBody.h=obj.scale[2]

        # constraint
        for obj in self.oneSkinMesh.constraints:
            constraint=io.addConstraint()
            constraint.setName(obj[CONSTRAINT_NAME].encode('cp932'))
            constraint.rigidA=rigidNameMap[obj[CONSTRAINT_A]]
            constraint.rigidB=rigidNameMap[obj[CONSTRAINT_B]]
            constraint.pos.x=obj.location[0]
            constraint.pos.y=obj.location[2]
            constraint.pos.z=obj.location[1]
            constraint.rot.x=-obj.rotation_euler[0]
            constraint.rot.y=-obj.rotation_euler[2]
            constraint.rot.z=-obj.rotation_euler[1]
            constraint.constraintPosMin.x=obj[CONSTRAINT_POS_MIN][0]
            constraint.constraintPosMin.y=obj[CONSTRAINT_POS_MIN][1]
            constraint.constraintPosMin.z=obj[CONSTRAINT_POS_MIN][2]
            constraint.constraintPosMax.x=obj[CONSTRAINT_POS_MAX][0]
            constraint.constraintPosMax.y=obj[CONSTRAINT_POS_MAX][1]
            constraint.constraintPosMax.z=obj[CONSTRAINT_POS_MAX][2]
            constraint.constraintRotMin.x=obj[CONSTRAINT_ROT_MIN][0]
            constraint.constraintRotMin.y=obj[CONSTRAINT_ROT_MIN][1]
            constraint.constraintRotMin.z=obj[CONSTRAINT_ROT_MIN][2]
            constraint.constraintRotMax.x=obj[CONSTRAINT_ROT_MAX][0]
            constraint.constraintRotMax.y=obj[CONSTRAINT_ROT_MAX][1]
            constraint.constraintRotMax.z=obj[CONSTRAINT_ROT_MAX][2]
            constraint.springPos.x=obj[CONSTRAINT_SPRING_POS][0]
            constraint.springPos.y=obj[CONSTRAINT_SPRING_POS][1]
            constraint.springPos.z=obj[CONSTRAINT_SPRING_POS][2]
            constraint.springRot.x=obj[CONSTRAINT_SPRING_ROT][0]
            constraint.springRot.y=obj[CONSTRAINT_SPRING_ROT][1]
            constraint.springRot.z=obj[CONSTRAINT_SPRING_ROT][2]

        # 書き込み
        bl.message('write: %s' % path)
        return io.write(path)


def __execute(filename):
    active=bl.object.getActive()
    if not active:
        print("abort. no active object.")
        return
    exporter=PmdExporter()
    exporter.setup()
    print(exporter)
    exporter.write(filename)
    bl.object.activate(active)


if isBlender24():
    # for 2.4
    def execute_24(filename):
        bl.initialize('pmd_export', bpy.data.scenes.active)
        __execute(filename.decode(bl.INTERNAL_ENCODING))
        bl.finalize()

    Blender.Window.FileSelector(
             execute_24,
             'Export Metasequoia PMD',
             Blender.sys.makename(ext='.pmd'))

else:
    # for 2.5
    def execute_25(filename, scene):
        bl.initialize('pmd_export', scene)
        __execute(filename)
        bl.finalize()

    # operator
    class EXPORT_OT_pmd(bpy.types.Operator):
        '''Save a Metasequoia PMD file.'''
        bl_idname = "export_scene.pmd"
        bl_label = 'Export PMD'

        # List of operator properties, the attributes will be assigned
        # to the class instance from the operator settings before calling.
        filepath = bpy.props.StringProperty()
        filename = bpy.props.StringProperty()
        directory = bpy.props.StringProperty()

        def execute(self, context):
            execute_25(
                    self.properties.filepath, 
                    context.scene
                    )
            return 'FINISHED'

        def invoke(self, context, event):
            wm=context.window_manager
            try:
                wm.fileselect_add(self)
            except:
                wm.add_fileselect(self)
            return 'RUNNING_MODAL'

    # register menu
    def menu_func(self, context): 
        default_path=bpy.data.filepath.replace(".blend", ".pmd")
        self.layout.operator(
                EXPORT_OT_pmd.bl_idname, 
                text="Miku Miku Dance Model(.pmd)",
                icon='PLUGIN'
                ).filepath=default_path

    def register():
        bpy.types.INFO_MT_file_export.append(menu_func)

    def unregister():
        bpy.types.INFO_MT_file_export.remove(menu_func)

    if __name__ == "__main__":
        register()

