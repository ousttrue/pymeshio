# coding: utf-8
"""
Blenderのメッシュをワンスキンメッシュ化する
"""
import bpy

from . import bl
from .pymeshio import englishmap

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
        return int(100*(self.nx + self.ny + self.nz + self.u + self.v))

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


class SSS(object):
    def __init__(self):
        self.use=1


class DefaultMatrial(object):
    def __init__(self):
        self.name='default'
        # diffuse
        self.diffuse_color=[1, 1, 1]
        self.alpha=1
        # specular
        self.specular_toon_size=0
        self.specular_hardness=5
        self.specular_color=[1, 1, 1]
        # ambient
        self.mirror_color=[1, 1, 1]
        # flag
        self.subsurface_scattering=SSS()
        # texture
        self.texture_slots=[]


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
        for i, v in enumerate(mesh.vertices):
            if len(v.groups)>0:
                for g in v.groups:
                    setWeight(i, obj.vertex_groups[g.group].name, g.weight)
            else:
                try:
                    setWeight(i, obj.vertex_groups[0].name, 1)
                except:
                    # no vertex_groups
                    pass

        # 合計値が1になるようにする
        for i in range(len(mesh.vertices)):
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
        default_material=DefaultMatrial()
        # 各面の処理
        for i, face in enumerate(mesh.faces):
            faceVertexCount=bl.face.getVertexCount(face)
            try:
                material=mesh.materials[bl.face.getMaterialIndex(face)]
            except IndexError as e:
                material=default_material
            v=[mesh.vertices[index] for index in bl.face.getVertices(face)]
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
        if bl.RIGID_SHAPE_TYPE in obj:
            return
        if bl.CONSTRAINT_A in obj:
            return

        bl.message("export: %s" % obj.name)

        # メッシュのコピーを生成してオブジェクトの行列を適用する
        copyMesh, copyObj=bl.object.duplicate(obj)
        if len(copyMesh.vertices)>0:
            # apply transform
            """
            try:
                # svn 36722
                copyObj.scale=obj.scale
                bpy.ops.object.transform_apply(scale=True)
                copyObj.rotation_euler=obj.rotation_euler
                bpy.ops.object.transform_apply(rotation=True)
                copyObj.location=obj.location
                bpy.ops.object.transform_apply(location=True)
            except AttributeError as e:
                # 2.57b
                copyObj.scale=obj.scale
                bpy.ops.object.scale_apply()
                copyObj.rotation_euler=obj.rotation_euler
                bpy.ops.object.rotation_apply()
                copyObj.location=obj.location
                bpy.ops.object.location_apply()
            """
            copyMesh.transform(obj.matrix_world)

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
        vg=bl.object.getVertexGroup(obj, bl.MMD_SHAPE_GROUP_NAME)

        # base
        used=set()
        for b in bl.object.getShapeKeys(obj):
            if b.name==bl.BASE_SHAPE_NAME:
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
        #print(basis.name, len(baseMorph.offsets))

        if len(baseMorph.offsets)==0:
            return

        # shape keys
        for b in bl.object.getShapeKeys(obj):
            if b.name==bl.BASE_SHAPE_NAME:
                continue

            #print(b.name)
            morph=self.__getOrCreateMorph(b.name, 4)
            used=set()
            for index, src, dst in zip(
                    range(len(blenderMesh.vertices)),
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
            #print(morph)
            return len(englishmap.skinMap)
        self.morphList.sort(key=getIndex)

    def __rigidbody(self, obj):
        if not bl.RIGID_SHAPE_TYPE in obj:
            return
        self.rigidbodies.append(obj)

    def __constraint(self, obj):
        if not bl.CONSTRAINT_A in obj:
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
            try:
                return self.getIndex(self.__boneByName(name))
            except:
                return 0

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


class Node(object):
    __slots__=['o', 'children']
    def __init__(self, o):
        self.o=o
        self.children=[]



class Exporter(object):

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
        self.englishComment=o[bl.MMD_COMMENT] if bl.MMD_COMMENT in o else 'blender export\n'
        self.name=o[bl.MMD_MB_NAME] if bl.MMD_MB_NAME in o else 'Blenderエクスポート'
        self.comment=o[bl.MMD_MB_COMMENT] if bl.MMD_MB_COMMENT in o else 'Blnderエクスポート\n'

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

