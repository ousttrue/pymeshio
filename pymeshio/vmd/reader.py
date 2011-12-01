# coding: utf-8
"""
vmd reader
"""
import io
import struct
from .. import common
from .. import vmd


class Reader(common.BinaryReader):
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

    def read_bone_frame(self):
        """
        フレームひとつ分を読み込む
        """
        frame=vmd.BoneFrame(self.read_text(15))
        (frame.frame, frame.pos.x, frame.pos.y, frame.pos.z,
        frame.q.x, frame.q.y, frame.q.z, frame.q.w) = struct.unpack(
                'I7f', self.ios.read(32))
        # complement data
        frame.complement=''.join(
                ['%x' % x for x in struct.unpack('64B', self.ios.read(64))])
        return frame

    def read_morph_frame(self):
        """
        モーフデータひとつ分を読み込む
        """
        frame=vmd.MorphFrame(self.read_text(15))
        (frame.frame, frame.ratio)=struct.unpack('If', self.ios.read(8))
        return frame


def read_from_file(path):
    """
    read from file path

    :Parameters:
      path
        file path

    >>> import vmd.reader
    >>> m=vmd.reader.read_from_file('resources/motion.vmd')
    >>> print(m)

    """
    return read(io.BytesIO(common.readall(path)))


def read(ios):
    assert(isinstance(ios, io.IOBase))
    reader=common.BinaryReader(ios)

    signature=reader.unpack("30s", 30)
    version=None
    if signature[:25] == "Vocaloid Motion Data 0002":
        version=2
    elif signature[:25] == "Vocaloid Motion Data file":
        version=1
    else:
        print("invalid signature", signature)
        return

    reader=Reader(reader.ios)
    motion=vmd.Motion()
    motion.model_name=reader.read_text(20)
    motion.motions=[reader.read_bone_frame() 
            for _ in range(reader.unpack('I', 4))]
    motion.shapes=[reader.read_morph_frame() 
            for _ in range(reader.unpack('I', 4))]
    motion.cameras=[reader.read_cameta_frame() 
            for _ in range(reader.unpack('I', 4))]
    motion.lights=[reader.read_light_frame() 
            for _ in range(reader.unpack('I', 4))]
    return motion

