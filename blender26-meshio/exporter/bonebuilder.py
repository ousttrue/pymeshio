# coding: utf-8
from .. import bl
from ..pymeshio import englishmap


class IKChain(object):
    __slots__=['index', 'limitAngle', 'limitMin', 'limitMax']
    def __init__(self, index, limitAngle, limitMin, limitMax):
        self.index=index
        self.limitAngle=limitAngle
        self.limitMin=limitMin
        self.limitMax=limitMax


class IKSolver(object):
    __slots__=['target_index', 'effector_index', 'iterations', 'weight', 'chain']
    def __init__(self, target_index, effector_index, iterations, weight):
        self.target_index=target_index
        self.effector_index=effector_index
        self.iterations=iterations
        self.weight=weight
        self.chain=[]

    def __str__(self):
        return "<IKSolver %d->%d, %d times(%f)>" % (
                self.target_index, self.effector_index,
                self.iterations, self.weight)


CONSTRAINT_NONE=0
CONSTRAINT_IK=1
CONSTRAINT_COPY_ROTATION=2
CONSTRAINT_LIMIT_ROTATION=3
CONSTRAINT_LIMIT_TRANSLATION=4
class Bone(object):
    __slots__=['index', 'name', 'english_name', 'ik_index',
            'ikSolver',
            'ikEffector',
            'pos', 'tail', 'parent_index', 'tail_index',
            'isVisible', 'hasTail', 
            'fixed_axis',
            'canTranslate',
            'constraint',
            'constraintTarget',
            'constraintInfluence',
            ]
    def __init__(self, index, name, english_name, pos, isVisible):
        self.index=index
        self.name=name
        self.english_name=english_name
        self.pos=pos
        self.tail=None
        self.parent_index=None
        self.tail_index=None
        self.isVisible=isVisible
        self.hasTail=False
        self.canTranslate=False
        self.ikSolver=None
        self.ikEffector=None
        #
        self.constraint=CONSTRAINT_NONE
        self.constraintTarget=0
        self.constraintInfluence=0

    def __eq__(self, rhs):
        return self.index==rhs.index

    def __str__(self):
        return "<Bone %s>" % (self.name)

    def isFixedAxis(self):
        return self.constraint==CONSTRAINT_LIMIT_ROTATION

    def canManipulate(self):
        return True


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
        self.bones=[Bone(i, 
            b.name, b.get(bl.BONE_ENGLISH_NAME, 'bone%04d' % i),
            bl.bone.getHeadLocal(b),
            not b.hide
            ) for i, b in enumerate(armature.bones.values())]
        for bone in self.bones:
            self.boneMap[bone.name]=bone

        # buid tree hierarchy
        def __getBone(bone, b):
            bone.hasTail=not (bl.BONE_USE_TAILOFFSET in b)

            if len(b.children)==0:
                return

            for i, c in enumerate(b.children):
                child=self.boneMap[c.name]
                if bone:
                    child.parent_index=bone.index
                __getBone(child, c)

        for bone, b in zip(self.bones, armature.bones.values()):
            if not b.parent:
                # root bone
                __getBone(bone, b)

        ####################
        # get pose bone info
        ####################
        pose = bl.object.getPose(armatureObj)
        for b in pose.bones.values():
            bone=self.boneMap[b.name]
            ####################
            # assing bone group
            ####################
            self.__assignBoneGroup(b, b.bone_group)

            # translation lock
            if not b.lock_location[0]:
                bone.canTranslate=True

            for c in b.constraints:
                if bl.constraint.isIKSolver(c):
                    # IK effector
                    ####################
                    # IK 接続先
                    effector=self.__boneByName(b.name)
                    effector.ikEffector=True

                    # IK solver
                    ####################
                    target=self.__boneByName(bl.constraint.ikTarget(c))
                    target.ikSolver=IKSolver(target.index, effector.index, 
                                int(c.iterations * 0.1), 
                                armature.bones[target.name].get(bl.IK_UNITRADIAN, 0)
                                )
                    # ik chain
                    ####################
                    chain=b.parent
                    chainLength=bl.constraint.ikChainLen(c)
                    for i in range(chainLength):
                        limit_anlge=False
                        limit_min=[0, 0, 0]
                        limit_max=[0, 0, 0]
                        if chain.use_ik_limit_x:
                            limit_anlge=True
                            # right handed to left handed ?
                            limit_min[0]=-chain.ik_max_x
                            limit_max[0]=-chain.ik_min_x
                        if chain.use_ik_limit_y:
                            limit_anlge=True
                            limit_min[1]=chain.ik_min_y
                            limit_max[1]=chain.ik_max_y
                        if chain.use_ik_limit_z:
                            limit_anlge=True
                            limit_min[2]=chain.ik_min_z
                            limit_max[2]=chain.ik_max_z
                        # IK影響下
                        target.ikSolver.chain.append(IKChain(
                            self.__boneByName(chain.name).index,
                            limit_anlge, limit_min, limit_max))
                        # next
                        chain=chain.parent

                if bl.constraint.isCopyRotation(c):
                    # copy rotation
                    bone.constraint=CONSTRAINT_COPY_ROTATION
                    bone.constraintTarget=c.subtarget
                    bone.constraintInfluence=c.influence

                if bl.constraint.isLimitRotation(c):
                    bone.constraint=CONSTRAINT_LIMIT_ROTATION

                if bl.constraint.isLimitTranslation(c):
                    bone.constraint=CONSTRAINT_LIMIT_TRANSLATION

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
                    return i
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
            if b.ikSolver:
                solver=b.ikSolver
                solver.target_index=sortMap[solver.target_index]
                solver.effector_index=sortMap[solver.effector_index]
                for c in solver.chain:
                    c.index=sortMap[c.index]

    def _fix(self):
        """
        調整
        """
        # set parent_index and tail_index
        for b in self.bones:
            if b.parent_index==None:
                b.parent_index=-1
            else:
                parent_b=self.bones[b.parent_index]
                if b.constraint==CONSTRAINT_LIMIT_TRANSLATION:
                    if parent_b.isFixedAxis():
                        self.bones[parent_b.parent_index].tail_index=b.index
                        parent_b.tail=[l - r for l, r in zip(b.pos, parent_b.pos)]
                    else:
                        parent_b.tail_index=b.index

        # set tail
        for b in self.bones:
            if not b.tail_index:
                b.tail_index=-1
                if not b.hasTail:
                    if not b.isFixedAxis():
                        b.tail=(0, 0, 0)
                    b.tail_index=-1

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


