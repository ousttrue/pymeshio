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
        reader.read_uint(1)
        model=pmm.Model()
        model.name=reader.read_text(20).decode('cp932')
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
        assert(n==1)
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

        # ボーン情報
        model.bones=[pmm.Bone(i) for i, b in enumerate(pmd_model.bones)]

        def read_boneframe(frame_index):
            f=pmm.BoneFrame(frame_index)

            # 57 byte
            f.frame_number=reader.read_int(4)
            f.prev_frame_index=reader.read_uint(4)
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

        return p

        # 51 byte
        reader.read_int(4)
        reader.read_int(4)
        reader.read_int(4)
        reader.read_int(4)
        reader.read_int(4)
        reader.read_int(4)
        reader.read_int(4)
        reader.read_int(4)
        reader.read_int(4)
        reader.read_int(4)
        reader.read_int(4)
        reader.read_int(4)
        reader.read_int(2)
        reader.read_int(1)

        # morph(init)
        morph_frame_count=reader.read_int(4)
        print 'morph_frame_count', morph_frame_count, reader
        for i, m in enumerate(pmd_model.morphs):
            # 17byte
            flag=reader.read_uint(1)
            print 'morph(init)', i, flag, reader
            reader.read_uint(1)
            reader.read_uint(1)
            reader.read_uint(1)

            reader.read_uint(1)
            reader.read_uint(1)
            reader.read_uint(1)
            reader.read_uint(1)

            reader.read_uint(1)
            reader.read_uint(1)
            reader.read_uint(1)
            reader.read_uint(1)
            expression=reader.read_float()
            is_selected=reader.read_uint(1)

        # morph(frames)
        print reader
        for i in range(morph_frame_count):
            print 'morph(frame)'
            reader.read_int(4)
            frame_number=reader.read_int(4)
            morph_index=reader.read_int(4)
            reader.read_int(4)
            expression=reader.read_float()
            is_selected=reader.read_uint(1)

        # frame state
        print reader
        #reader.read_int(4)
        #reader.read_int(4)
        #reader.read_int(2)
        #reader.read_int(4)
        #reader.read_int(4)
        #is_visible=reader.read_uint(1)
        [reader.read_uint(1) for ik in pmd_model.ik_list]
        #is_selected=reader.read_uint(1)

        #model_state_count=reader.read_int(4)
        #print 'model_state_count', model_state_count
        #for i in range(model_state_count):
        #    print 'state', i
        #    index=reader.read_int(4)
        #    frame_number=reader.read_int(4)
        #    reader.read_int(4)
        #    reader.read_int(4)
        #    is_visible=reader.read_uint(1)
        #    [reader.read_uint(1) for ik in pmd_model.ik_list]
        #    is_selected=reader.read_uint(1)
        
        # edit
        # pose
        print reader
        for i, b in enumerate(pmd_model.bones):
            # 34 byte
            flag=reader.read_uint(1)
            print 'edit(bone)', i, flag, reader
            edit_pos=reader.read_vector3()
            edit_rot=reader.read_quaternion()
            reader.read_uint(1)
            reader.read_uint(1)
            reader.read_uint(1)
            is_changed=reader.read_uint(1)
            is_selected=reader.read_uint(1)
        # morph
        print reader
        for i, m in enumerate(pmd_model.morphs):
            expression=reader.read_float()
            print 'edit(morph)', i, expression
        # ik
        print reader
        for i, ik in enumerate(pmd_model.ik_list):
            is_enable=reader.read_uint(1)
            print 'edit(ik)', i, is_enable
            
    return p

