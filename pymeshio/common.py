# coding: utf-8
"""
common utilities.
"""
import math

def radian_to_degree(x):
    """darian to deglee"""

    return x/math.pi * 180.0


"""
common structures.
"""
class Vector2(object):
    """
    2D coordinate for uv value
    """
    __slots__=['x', 'y']
    def __init__(self, x=0, y=0):
        self.x=x
        self.y=y

    def __str__(self):
        return "<%f %f>" % (self.x, self.y)

    def __getitem__(self, key):
        if key==0:
            return self.x
        elif key==1:
            return self.y
        else:
            assert(False)

    def to_tuple(self):
        return (self.x, self.y)


class Vector3(object):
    """
    3D coordinate for vertex position, normal direction
    """
    __slots__=['x', 'y', 'z']
    def __init__(self, x=0, y=0, z=0):
        self.x=x
        self.y=y
        self.z=z

    def __str__(self):
        return "<%f %f %f>" % (self.x, self.y, self.z)

    def __getitem__(self, key):
        if key==0:
            return self.x
        elif key==1:
            return self.y
        elif key==2:
            return self.z
        else:
            assert(False)

    def to_tuple(self):
        return (self.x, self.y, self.z)

    def __add__(l, r):
        return Vector3(l.x+r.x, l.y+r.y, l.z+r.z)


class Quaternion(object):
    """
    rotation representation in vmd motion
    """
    __slots__=['x', 'y', 'z', 'w']
    def __init__(self, x=0, y=0, z=0, w=1):
        self.x=x
        self.y=y
        self.z=z
        self.w=w

    def __str__(self):
        return "<%f %f %f %f>" % (self.x, self.y, self.z, self.w)

    def __mul__(self, rhs):
        u=numpy.array([self.x, self.y, self.z], 'f')
        v=numpy.array([rhs.x, rhs.y, rhs.z], 'f')
        xyz=self.w*v+rhs.w*u+numpy.cross(u, v)
        q=Quaternion(xyz[0], xyz[1], xyz[2], self.w*rhs.w-numpy.dot(u, v))
        return q

    def dot(self, rhs):
        return self.x*rhs.x+self.y*rhs.y+self.z*rhs.z+self.w*rhs.w

    def getMatrix(self):
        sqX=self.x*self.x
        sqY=self.y*self.y
        sqZ=self.z*self.z
        xy=self.x*self.y
        xz=self.x*self.z
        yz=self.y*self.z
        wx=self.w*self.x
        wy=self.w*self.y
        wz=self.w*self.z
        return numpy.array([
                # 1
                [1-2*sqY-2*sqZ, 2*xy+2*wz, 2*xz-2*wy, 0],
                # 2
                [2*xy-2*wz, 1-2*sqX-2*sqZ, 2*yz+2*wx, 0],
                # 3
                [2*xz+2*wy, 2*yz-2*wx, 1-2*sqX-2*sqY, 0],
                # 4
                [0, 0, 0, 1]],
                'f')

    def getRHMatrix(self):
        x=-self.x
        y=-self.y
        z=self.z
        w=self.w
        sqX=x*x
        sqY=y*y
        sqZ=z*z
        xy=x*y
        xz=x*z
        yz=y*z
        wx=w*x
        wy=w*y
        wz=w*z
        return numpy.array([
                # 1
                [1-2*sqY-2*sqZ, 2*xy+2*wz, 2*xz-2*wy, 0],
                # 2
                [2*xy-2*wz, 1-2*sqX-2*sqZ, 2*yz+2*wx, 0],
                # 3
                [2*xz+2*wy, 2*yz-2*wx, 1-2*sqX-2*sqY, 0],
                # 4
                [0, 0, 0, 1]],
                'f')

    def getRollPitchYaw(self):
        m=self.getMatrix()

        roll = math.atan2(m[0, 1], m[1, 1])
        pitch = math.asin(-m[2, 1])
        yaw = math.atan2(m[2, 0], m[2, 2])

        if math.fabs(math.cos(pitch)) < 1.0e-6:
            roll += m[0, 1] > math.pi if 0.0 else -math.pi
            yaw += m[2, 0] > math.pi if 0.0 else -math.pi

        return roll, pitch, yaw

    def getSqNorm(self):
        return self.x*self.x+self.y*self.y+self.z*self.z+self.w*self.w

    def getNormalized(self):
        f=1.0/self.getSqNorm()
        q=Quaternion(self.x*f, self.y*f, self.z*f, self.w*f)
        return q

    def getRightHanded(self):
        "swap y and z axis"
        return Quaternion(-self.x, -self.z, -self.y, self.w)

    @staticmethod
    def createFromAxisAngle(axis, rad):
        q=Quaternion()
        half_rad=rad/2.0
        c=math.cos(half_rad)
        s=math.sin(half_rad)
        return Quaternion(axis[0]*s, axis[1]*s, axis[2]*s, c)


class RGBA(object):
    """
    material color
    """
    __slots__=['r', 'g', 'b', 'a']
    def __init__(self, r=0, g=0, b=0, a=1):
        self.r=r
        self.g=g
        self.b=b
        self.a=a

    def __getitem__(self, key):
        if key==0:
            return self.r
        elif key==1:
            return self.g
        elif key==2:
            return self.b
        elif key==3:
            return self.a
        else:
            assert(False)

