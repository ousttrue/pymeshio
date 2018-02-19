import struct


class BytesReader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def get_bytes(self, size: int)->bytes:
        res = self.data[self.pos:self.pos + size]
        self.pos += size
        return res

    def get_uint32(self)->int:
        return struct.unpack('I', self.get_bytes(4))[0]

    def get_float(self)->float:
        return struct.unpack('f', self.get_bytes(4))[0]

    def get_str(self, size: int, encoding: str)->str:
        data = self.get_bytes(size)
        pos = data.index(0)
        if pos == -1:
            return data.decode(encoding)
        else:
            return data[0:pos].decode(encoding)
