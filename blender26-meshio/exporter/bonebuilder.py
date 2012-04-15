# coding: utf-8
from .. import bl
from ..pymeshio import englishmap


class IKSolver(object):
    __slots__=['target', 'effector', 'length', 'iterations', 'weight']
    def __init__(self, target, effector, length, iterations, weight):
        self.target=target
        self.effector=effector
        self.length=length
        self.iterations=iterations
        self.weight=weight


class Bone(object):
    __slots__=['index', 'name', 'ik_index',
            'pos', 'tail', 'parent_index', 'tail_index', 'type', 'isConnect']
    def __init__(self, index, name, pos, tail, isConnect):
        self.index=index
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
        # create bones
        ####################
        self.bones=[Bone(i, b.name,
            bl.bone.getHeadLocal(b),
            bl.bone.getTailLocal(b),
            False) for i, b in enumerate(armature.bones.values())]
        for bone in self.bones:
            self.boneMap[bone.name]=bone

        # buid tree hierarchy
        def __getBone(parent, b):
            if len(b.children)==0:
                parent.type=7
                return

            for i, c in enumerate(b.children):
                bone=self.boneMap[c.name]
                bone.isConnect=bl.bone.isConnected(c)
                if parent:
                    bone.parent_index=parent.index
                    #if i==0:
                    if bone.isConnect or (
                            not parent.tail_index and parent.tail==bone.pos):
                        parent.tail_index=bone.index
                __getBone(bone, c)

        for b in armature.bones.values():
            if not b.parent:
                # root bone
                __getBone(bone, b)

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

    def _sortBy(self):
        """
        boneMap順に並べ替える
        """
        boneMap=englishmap.boneMap
        original=self.bones[:]
        def getIndex(bone):
            for i, k_v in enumerate(boneMap):
                if (k_v[0]==bone.name or k_v[1]==bone.name):
                    print(bone.name)
                    return i
            #print(bone)
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
                b.parent_index=-1
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


