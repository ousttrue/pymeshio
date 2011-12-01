# coding: utf-8
"""
vmd reader
"""
import io
from .. import common
from .. import vmd


class VMDLoader(object):
    __slots__=['io', 'end', 'signature',
            'model_name', 'last_frame',
            'motions', 'shapes', 'cameras', 'lights',
            ]
    def __init__(self):
        self.model_name=''
        self.motions=[]
        self.shapes=[]
        self.cameras=[]
        self.lights=[]
        self.last_frame=0

    def __str__(self):
        return '<VMDLoader model: "%s", motion: %d, shape: %d, camera: %d, light: %d>' % (
            self.model_name, len(self.motions), len(self.shapes),
            len(self.cameras), len(self.lights))

    def load(self, path, io, end):
        self.io=io
        self.end=end

        # signature
        self.signature=truncate_zero(self.io.read(30))
        version=self.validate_signature(self.signature)
        if not version:
            print("invalid signature", self.signature)
            return False

        if version==1:
            if not self.load_verstion_1():
                return False
        elif version==2:
            if not  self.load_verstion_2():
                return False 
        else:
            raise Exception("unknown version") 

        # post process
        motions=self.motions
        self.motions={}
        for m in motions:
            if not m.name in self.motions:
                self.motions[m.name]=[]
            self.motions[m.name].append(m)
        for name in self.motions.keys():
            self.motions[name].sort()

        shapes=self.shapes
        self.shapes={}
        for s in shapes:
            if not s.name in self.shapes:
                self.shapes[s.name]=[]
            self.shapes[s.name].append(s)
        for name in self.shapes.keys():
            self.shapes[name].sort()

        return True

    def getMotionCount(self):
        count=0
        for v in self.motions.values():
            count+=len(v)
        return count

    def getShapeCount(self):
        count=0
        for v in self.shapes.values():
            count+=len(v)
        return count

    def load_verstion_1(self):
        # model name
        self.model_name=truncate_zero(self.io.read(10))
        if not self.loadMotion_1():
            return False
        return True

    def loadMotion_1(self):
        count=struct.unpack('H', self.io.read(2))[0]
        self.io.read(2)
        for i in xrange(0, count):
            self.loadFrameData()
        return True

    ############################################################
    def load_verstion_2(self):
        # model name
        self.model_name=truncate_zero(self.io.read(20))

        if not self.loadMotion():
            return False
        if not self.loadShape():
            return False
        if not self.loadCamera():
            return False
        if not self.loadLight():
            return False
        #assert(self.io.tell()==self.end)
        #self.motions.sort(lambda l, r: l.name<r.name)

        return True

    def validate_signature(self, signature):
        if self.signature == "Vocaloid Motion Data 0002":
            return 2
        if self.signature == "Vocaloid Motion Data file":
            return 1
        else:
            return None

    def loadMotion(self):
        count=struct.unpack('I', self.io.read(4))[0]
        for i in xrange(0, count):
            self.loadFrameData()
        return True

    def loadShape(self):
        count=struct.unpack('I', self.io.read(4))[0]
        for i in xrange(0, count):
            self.loadShapeData()
        return True

    def loadCamera(self):
        count=struct.unpack('I', self.io.read(4))[0]
        for i in xrange(0, count):
            # not implemented
            assert(False)
            pass
        return True

    def loadLight(self):
        count=struct.unpack('I', self.io.read(4))[0]
        for i in xrange(0, count):
            # not implemented
            assert(False)
            pass
        return True

    def loadFrameData(self):
        """
        フレームひとつ分を読み込む
        """
        data=MotionData(truncate_zero(self.io.read(15)))
        (data.frame, data.pos.x, data.pos.y, data.pos.z,
        data.q.x, data.q.y, data.q.z, data.q.w) = struct.unpack(
                'I7f', self.io.read(32))
        # complement data
        data.complement=''.join(
                ['%x' % x for x in struct.unpack('64B', self.io.read(64))])
        self.motions.append(data)
        if data.frame>self.last_frame:
            self.last_frame=data.frame

    def loadShapeData(self):
        """
        モーフデータひとつ分を読み込む
        """
        data=ShapeData(truncate_zero(self.io.read(15)))
        (data.frame, data.ratio)=struct.unpack('If', self.io.read(8))
        self.shapes.append(data)
        if data.frame>self.last_frame:
            self.last_frame=data.frame

    # vmd -> csv
    ############################################################
    def create_csv_line(m):
        # quaternion -> euler angle
        (roll, pitch, yaw)=m.q.getRollPitchYaw()
        return '%s,%d,%g,%g,%g,%g,%g,%g,0x%s\n' % (
                m.name, m.frame, m.pos.x, m.pos.y, m.pos.z,
                to_degree(pitch), to_degree(yaw), to_degree(roll), m.complement
                )

    def write_csv(l, path):
        sys.setdefaultencoding('cp932')
        csv=open(path, "w")
        csv.write('%s,0\n' % l.signature)
        csv.write('%s\n' % l.model_name)
        # motion
        csv.write('%d\n' % len(l.motions))
        for m in l.motions:
            csv.write(create_csv_line(m))
        # shape
        csv.write('%d\n' % len(l.shapes))
        for s in l.shapes:
            csv.write('%s,%d,%f\n' % ( s.name, s.frame, s.ratio))
        # camera
        csv.write('%d\n' % len(l.cameras))
        for camera in l.cameras:
            assert(False)
        # light
        csv.write('%d\n' % len(l.lights))
        for light in l.lights:
            assert(False)

