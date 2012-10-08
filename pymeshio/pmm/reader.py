# coding: utf-8
import io
import os
import sys
from .. import common
from .. import pmm
from .. import pmd
from ..pmd import reader as pmd_reader


class Reader(common.BinaryReader):
    """pmx reader
    """
    def __init__(self, ios):
        super(Reader, self).__init__(ios)

    def read_text(self, size):
        """read cp932 text
        """
        src=self.unpack("%ds" % size, size)
        assert(type(src)==bytes)
        pos = src.find(b"\x00")
        if pos==-1:
            return src
        else:
            return src[:pos]


def read_from_file(path):
    """
    read from file path

    :Parameters:
      path
        file path

    >>> import pmm.reader
    >>> m=pmm.reader.read_from_file('resources/UserFile/きしめん.pmm')
    >>> print(m)

    """
    assert(isinstance(path, unicode))
    pmm=read(io.BytesIO(common.readall(path)), os.path.dirname(path))
    pmm.path=path
    return pmm


def read(ios, base_dir):
    """
    read from ios

    :Parameters:
      ios
        input stream (in io.IOBase)

    >>> import pmm.reader
    >>> m=pmm.reader.read(io.open('resources/UserFile/きしめん.pmm', 'rb'))
    >>> print(m)

    """
    assert(isinstance(ios, io.IOBase))
    reader=Reader(ios)

    # header
    signature=reader.read_text(30)
    if signature!=b"Polygon Movie maker 0001":
        raise common.ParseException(
                "invalid signature", signature)

    p=pmm.Project()
    p.screen_width=reader.read_int(4)
    p.screen_height=reader.read_int(4)
    p.timeline_view_width=reader.read_int(4)

    # unknown
    reader.read_uint(1)
    reader.read_uint(1)
    reader.read_uint(1)
    reader.read_uint(1)

    p.is_camera_mode=reader.read_uint(1)

    # unknown
    reader.read_uint(1)
    reader.read_uint(1)
    reader.read_uint(1)
    reader.read_uint(1)
    reader.read_uint(1)
    reader.read_uint(1)

    model_count=reader.read_uint(1)
    model_names=[reader.read_text(20).decode('cp932') for _ in range(model_count)]
    for i in range(model_count):
        print 'model', reader

        reader.read_uint(1)
        model=pmm.Model()
        model.name=reader.read_text(20).decode('cp932')
        print 'name', model.name
        model.path=reader.read_text(256).decode('cp932')
        # path - base_dir
        pos=model.path.index("\\UserFile\\")
        model.path=model.path[pos+10:]
        # 該当pmd読み込み
        pmd_model=pmd_reader.read_from_file(os.path.join(base_dir, model.path))

        # unknown
        reader.read_uint(1)

        model.is_visible=reader.read_uint(1)

        # unknown
        reader.read_int(4)
        n=reader.read_int(4)
        #assert(n==1)
        reader.read_int(4)
        reader.read_int(4)
        reader.read_int(4)

        # nazo
        nazo_count=reader.read_uint(1)
        print 'nazo_count', nazo_count
        nazo=[reader.read_uint(1) for _ in range(nazo_count)]
        print nazo

        # ?
        reader.read_uint(1)
        reader.read_uint(1)
        reader.read_uint(1)
        reader.read_uint(1)

        max_frame_number=reader.read_uint(4)
        print 'max_frame_number', max_frame_number, reader

        ############################################################
        # ボーン情報
        model.bones=[pmm.Bone(i) for i, b in enumerate(pmd_model.bones)]

        def read_boneframe(frame_index):
            f=pmm.BoneFrame(frame_index)

            # 57 byte
            f.frame_number=reader.read_int(4)
            f.prev_frame_index=reader.read_int(4)
            f.next_frame_index=reader.read_int(4)
            # next_frame_index!=0の場合次のフレームがある

            # icrv1
            reader.read_uint(1)
            reader.read_uint(1)
            reader.read_uint(1)
            reader.read_uint(1)
            # icrv2
            reader.read_uint(1)
            reader.read_uint(1)
            reader.read_uint(1)
            reader.read_uint(1)
            # icrv3
            reader.read_uint(1)
            reader.read_uint(1)
            reader.read_uint(1)
            reader.read_uint(1)
            # icrv4
            reader.read_uint(1)
            reader.read_uint(1)
            reader.read_uint(1)
            reader.read_uint(1)

            f.pos=reader.read_vector3()
            f.rot=reader.read_quaternion()
            f.is_selected=reader.read_uint(1)

            print f
            return f

        # ボーンの初期位置
        # ボーンの数だけある
        b.frames=[read_boneframe(i) for i, b in enumerate(model.bones)]

        # 後続のボーンフレーム数
        remain_bone_frame_count=reader.read_int(4)
        print 'remain_bone_frame_count', remain_bone_frame_count

        # ボーンのフレーム情報
        for i in range(remain_bone_frame_count):
            frame_index=reader.read_int(4)
            f=read_boneframe(frame_index)


        ############################################################
        # morph(init)
        def read_morphframe(frame_index):
            f=pmm.MorphFrame(frame_index)

            # 17byte
            f.frame_number=reader.read_int(4)
            f.prev_frame_index=reader.read_int(4)
            f.next_frame_index=reader.read_int(4)
            # next_frame_index!=0の場合次のフレームがある
            f.expression=reader.read_float()
            f.is_selected=reader.read_uint(1)

            print f

        for i, m in enumerate(pmd_model.morphs):
            # morph(frames)
            read_morphframe(i)

        remain_morph_frame_count=reader.read_int(4)
        print 'remain_morph_frame_count', remain_morph_frame_count

        for i in range(remain_morph_frame_count):
            index=reader.read_int(4)
            read_morphframe(index)

        ############################################################
        # model state
        print reader

        def read_stateframe(frame_index):
            f=pmm.StateFrame(frame_index)
            f.frame_number=reader.read_int(4)
            f.prev_frame_index=reader.read_int(4)
            f.next_frame_index=reader.read_int(4)

            f.is_visible=reader.read_uint(1)
            f.ik_enables=[reader.read_uint(1) for ik in pmd_model.ik_list]
            f.is_selected=reader.read_uint(1)

            print f

        read_stateframe(0)

        model_state_frame_count=reader.read_int(4)
        print 'model_state_frame_count', model_state_frame_count
        for i in range(model_state_frame_count):
            index=reader.read_int(4)
            read_stateframe(index)
        
        ############################################################
        # edit
        # pose
        print 'bone', reader
        for i, b in enumerate(pmd_model.bones):
            # 34 byte
            edit_pos=reader.read_vector3()
            edit_rot=reader.read_quaternion()
            reader.read_int(4)
            is_changed=reader.read_uint(1)
            is_selected=reader.read_uint(1)

        # morph
        print 'morph', reader
        for i, m in enumerate(pmd_model.morphs):
            #print i, m
            expression=reader.read_float()

        # ik
        print 'ik', reader
        for i, ik in enumerate(pmd_model.ik_list):
            is_enable=reader.read_uint(1)

        print reader
        print

    ############################################################
    # camera
    def read_cameraframe(frame_index):
        f=pmm.CameraFrame(frame_index)
        f.frame_number=reader.read_int(4)
        f.prev_frame_index=reader.read_int(4)
        f.next_frame_index=reader.read_int(4)
        f.pos=reader.read_vector3()
        f.rot=reader.read_quaternion()
        # icrv1
        reader.read_uint(1)
        reader.read_uint(1)
        reader.read_uint(1)
        reader.read_uint(1)
        # icrv2
        reader.read_uint(1)
        reader.read_uint(1)
        reader.read_uint(1)
        reader.read_uint(1)
        # icrv3
        reader.read_uint(1)
        reader.read_uint(1)
        reader.read_uint(1)
        reader.read_uint(1)
        # icrv4
        reader.read_uint(1)
        reader.read_uint(1)
        reader.read_uint(1)
        reader.read_uint(1)
        # icrv5
        reader.read_uint(1)
        reader.read_uint(1)
        reader.read_uint(1)
        reader.read_uint(1)
        # icrvr
        reader.read_uint(1)
        reader.read_uint(1)
        reader.read_uint(1)
        reader.read_uint(1)

        is_selected=reader.read_uint(1)
        fovy=reader.read_uint(1)

        reader.read_int(4)

        print f

    read_cameraframe(0)

    camera_frame_count=reader.read_int(4)
    print 'camera_frame_count', camera_frame_count
    for i in range(camera_frame_count):
        index=reader.read_int(4)
        read_cameraframe(index)
 
    print reader

    ############################################################
    # light
    reader.read_text(37)
    print reader

    def read_lightframe(frame_index):
        f=pmm.LightFrame(frame_index)
        f.frame_number=reader.read_int(4)
        f.prev_frame_index=reader.read_int(4)
        f.next_frame_index=reader.read_int(4)

        reader.read_text(25)
        print f

    read_lightframe(0)

    light_frame_count=reader.read_int(4)
    print 'light_frame_count', light_frame_count
    for i in range(light_frame_count):
        index=reader.read_int(4)
        read_lightframe(index)
 
    print reader

    return p

