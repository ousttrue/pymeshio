# coding: utf-8
"""
========================
MikuMikuDance PMM format
========================

file format
~~~~~~~~~~~
http://v-nyappon.net/?m=diary&a=page_detail&target_c_diary_id=979053

"""
from .. import common


class BoneFrame(common.Diff):
    __slots__=[
            'next_frame_index',
            'prev_frame_index',
            'frame_number',
            'frame_index',
            ]
    def __init__(self, frame_index):
        self.frame_index=frame_index

    def __str__(self):
        return "<BoneFrame [%d] %d frame, [%d]<- ->[%d]>" % (
                self.frame_index, self.frame_number, 
                self.prev_frame_index, 
                self.next_frame_index)


class Bone(common.Diff):
    __slots__=[
            'frames',
            'index',
            ]
    def __init__(self, index):
        self.index=index
        self.frames=[]

    def __str__(self):
        return "<Bone "+",".join((str(f) for f in self.frames))+">"


class Model(common.Diff):
    __slots__=[
            'name',
            'path',
            'bones',
            ]
    def __init__(self):
        self.bones=[]

    def __str__(self):
        print self.name, len(self.name)
        print self.path, len(self.path)
        return u"<pmm.Model %s:%s>" % (self.name, self.path)

    def get_next_bone_by_next_frame_index(self, frame_index):
        for b in self.bones:
            for f in b.frames:
                if f.next_frame_index==frame_index:
                    return b


class Project(common.Diff):
    __slots__=[
            'path',
            'screen_width',
            'screen_height',
            'timelineview_width',
            'is_camera_mode',
            'models',
            ]
    def __init__(self):
        self.models=[]


