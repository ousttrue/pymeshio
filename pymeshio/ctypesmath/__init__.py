'''
ctypesmath(Linear Algebra Helper)

This library is row vector style and matrix use row major layout.
(DirectX style)

# mult order

pos = vec4 * Model * View * Projection
    = vec4 * MVP

# row major layout

| 0  1  2  3|
| 4  5  6  7|
| 8  9 10 11|
|12 13 14 15|

# glsl(col major)

glUniformMatrix4fv(loc, cnt, False, matrix)
(transposed)

## col major layout

| 0  4  8 12|
| 1  5  9 13|
| 2  6 10 14|
| 3  7 11 15|

GL_Position = PVM * vPosition;

# glsl(row major)

glUniformMatrix4fv(loc, cnt, True, matrix)
(not transposed)

GL_Position = vPosition * MVP;
'''


import math
import unittest
import ctypes
from typing import NamedTuple


class Float3(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
    ]
    def __getitem__(self, key):
        if key==0:
            return self.x
        elif key==1:
            return self.y
        elif key==2:
            return self.z
        else:
            raise IndexError()
    def __eq__(self, rhs):
        for l, r in zip(self, rhs):
            if math.fabs(l - r) > 1e-4:
                return False
        return True


class Float4(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
        ("z", ctypes.c_float),
        ("w", ctypes.c_float),
    ]
    def __getitem__(self, key):
        if key==0:
            return self.x
        elif key==1:
            return self.y
        elif key==2:
            return self.z
        elif key==3:
            return self.w
        else:
            raise IndexError()
    def __eq__(self, rhs):
        for l, r in zip(self, rhs):
            if math.fabs(l - r) > 1e-4:
                return False
        return True


class Float9(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("m00", ctypes.c_float),
        ("m01", ctypes.c_float),
        ("m02", ctypes.c_float),
        ("m10", ctypes.c_float),
        ("m11", ctypes.c_float),
        ("m12", ctypes.c_float),
        ("m20", ctypes.c_float),
        ("m21", ctypes.c_float),
        ("m22", ctypes.c_float),
    ]
    def __getitem__(self, key):
        if key==0:
            return self.m00
        elif key==1:
            return self.m01
        elif key==2:
            return self.m02
        elif key==3:
            return self.m10
        elif key==4:
            return self.m11
        elif key==5:
            return self.m12
        elif key==6:
            return self.m20
        elif key==7:
            return self.m21
        elif key==8:
            return self.m22
        else:
            raise IndexError()
    def __eq__(self, rhs):
        for l, r in zip(self, rhs):
            if math.fabs(l - r) > 1e-4:
                return False
        return True


class Float16(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("m00", ctypes.c_float),
        ("m01", ctypes.c_float),
        ("m02", ctypes.c_float),
        ("m03", ctypes.c_float),
        ("m10", ctypes.c_float),
        ("m11", ctypes.c_float),
        ("m12", ctypes.c_float),
        ("m13", ctypes.c_float),
        ("m20", ctypes.c_float),
        ("m21", ctypes.c_float),
        ("m22", ctypes.c_float),
        ("m23", ctypes.c_float),
        ("m30", ctypes.c_float),
        ("m31", ctypes.c_float),
        ("m32", ctypes.c_float),
        ("m33", ctypes.c_float),
    ]
    def __getitem__(self, key):
        if key==0:
            return self.m00
        elif key==1:
            return self.m01
        elif key==2:
            return self.m02
        elif key==3:
            return self.m03
        elif key==4:
            return self.m10
        elif key==5:
            return self.m11
        elif key==6:
            return self.m12
        elif key==7:
            return self.m13
        elif key==8:
            return self.m20
        elif key==9:
            return self.m21
        elif key==10:
            return self.m22
        elif key==11:
            return self.m23
        elif key==12:
            return self.m30
        elif key==13:
            return self.m31
        elif key==14:
            return self.m32
        elif key==15:
            return self.m33
        else:
            raise IndexError()
    def __eq__(self, rhs):
        for l, r in zip(self, rhs):
            if math.fabs(l - r) > 1e-4:
                return False
        return True


class Vec3(Float3):
    @staticmethod
    def zero()->'Vec3':
        return Vec3(0, 0, 0)

    @staticmethod
    def one()->'Vec3':
        return Vec3(1, 1, 1)

    def __add__(self, rhs)->'Vec3':
        return Vec3(self.x + rhs.x, self.y + rhs.y, self.z + rhs.z)

    def __sub__(self, rhs: 'Vec3')->'Vec3':
        return Vec3(self.x - rhs.x, self.y - rhs.y, self.z - rhs.z)

    def __mul__(self, factor: float)->'Vec3':
        return Vec3(self.x * factor, self.y * factor, self.z * factor)

    def dot(self, rhs)->float:
        return self.x * rhs.x + self.y * rhs.y + self.z * rhs.z

    def cross(self, rhs)->'Vec3':
        return Vec3(self.y * rhs.z - self.z * rhs.y,
                    self.z * rhs.x - self.x * rhs.z,
                    self.x * rhs.y - self.y * rhs.x)

    @property
    def sqnorm(self)->float: return self.dot(self)

    @property
    def norm(self)->float: return math.sqrt(self.sqnorm)

    @property
    def normalized(self): return self * (1 / self.norm)


class Vec4(Float4):
    @staticmethod
    def zero()->'Vec4':
        return Vec4(0, 0, 0, 0)

    @staticmethod
    def one()->'Vec4':
        return Vec4(1, 1, 1, 1)

    @property
    def vec3(self)->Vec3:
        return Vec3(self.x, self.y, self.z)

    @property
    def vec3_w_normalized(self)->Vec3:
        return Vec3(self.x / self.w, self.y / self.w, self.z / self.w)

    def __add__(self, rhs)->'Vec4':
        return Vec4(self.x + rhs.x, self.y + rhs.y, self.z + rhs.z, self.w + rhs.w)

    def __sub__(self, rhs: 'Vec4')->'Vec4':
        return Vec4(self.x - rhs.x, self.y - rhs.y, self.z - rhs.z, self.w - rhs.w)

    def dot(self, rhs)->float:
        return (self.x * rhs.x +
                self.y * rhs.y +
                self.z * rhs.z +
                self.w * rhs.w)


class Quaternion(Float4):
    @staticmethod
    def identity()->'Quaternion':
        return Quaternion(0, 0, 0, 1)

    @staticmethod
    def from_mat3(m: 'Mat3')->'Quaternion':
        w = math.sqrt(1.0 + m.m00 + m.m11 + m.m22) / 2.0
        w4 = 4 * w
        x = (m.m21 - m.m12) / w4
        y = (m.m02 - m.m20) / w4
        z = (m.m10 - m.m01) / w4
        return Quaternion(x, y, z, w)

    def to_mat3(self)->'Mat3':
        return Mat3(1 - 2 * self.y * self.y - 2 * self.z * self.z,
                    2 * self.x * self.y - 2 * self.w * self.z,
                    2 * self.x * self.z - 2 * self.w * self.y,

                    2 * self.x * self.y + 2 * self.w * self.z,
                    1 - 2 * self.x * self.x - 2 * self.z * self.z,
                    2 * self.y * self.z - 2 * self.w * self.x,

                    2 * self.x * self.z - 2 * self.w * self.y,
                    2 * self.y * self.z + 2 * self.w * self.x,
                    1 - 2 * self.x * self.x - 2 * self.y * self.y)
        '''
        return Mat3(1-2*self.y*self.y-2*self.z*self.z,
                    2*self.x*self.y+2*self.w*self.z,
                    2*self.x*self.z-2*self.w*self.y,

                    2*self.x*self.y-2*self.w*self.z,
                    1-2*self.x*self.x-2*self.z*self.z,
                    2*self.y*self.z+2*self.w*self.x,

                    2*self.x*self.z-2*self.w*self.y,
                    2*self.y*self.z-2*self.w*self.x,
                    1-2*self.x*self.x-2*self.y*self.y
                    )
        '''

    def __mul__(self, rhs)->'Quaternion':
        return Quaternion.from_mat3(self.to_mat3() * rhs.to_mat3())


class Mat3(Float9):
    @staticmethod
    def identity()->'Mat3':
        return Mat3(1, 0, 0,
                    0, 1, 0,
                    0, 0, 1)

    @staticmethod
    def rotation_x_axis_by_degree(degree: float)->'Mat3':
        rad = math.radians(degree)
        s = math.sin(rad)
        c = math.cos(rad)
        return Mat3(1, 0, 0,
                    0, c, s,
                    0, -s, c)

    @staticmethod
    def rotation_y_axis_by_degree(degree: float)->'Mat3':
        rad = math.radians(degree)
        s = math.sin(rad)
        c = math.cos(rad)
        return Mat3(c, 0, -s,
                    0, 1, 0,
                    s, 0, c)

    @staticmethod
    def rotation_z_axis_by_degree(degree: float)->'Mat3':
        rad = math.radians(degree)
        s = math.sin(rad)
        c = math.cos(rad)
        return Mat3(c, s, 0,
                    -s, c, 0,
                    0, 0, 1)

    def row(self, n)->Vec3:
        i = n * 3
        return Vec3(self[i], self[i + 1], self[i + 2])

    def col(self, n)->Vec3:
        return Vec3(self[n], self[n + 3], self[n + 6])

    def __mul__(self, rhs)->'Mat3':
        return Mat3(
            self.row(0).dot(rhs.col(0)),
            self.row(0).dot(rhs.col(1)),
            self.row(0).dot(rhs.col(2)),
            self.row(1).dot(rhs.col(0)),
            self.row(1).dot(rhs.col(1)),
            self.row(1).dot(rhs.col(2)),
            self.row(2).dot(rhs.col(0)),
            self.row(2).dot(rhs.col(1)),
            self.row(2).dot(rhs.col(2)))

    def apply(self, v: Vec3)->Vec3:
        return Vec3(v.dot(self.row(0)), v.dot(self.row(1)), v.dot(self.row(2)))


class Mat4(Float16):
    def row(self, n)->Vec4:
        i = n * 4
        return Vec4(self[i], self[i + 1], self[i + 2], self[i + 3])

    def col(self, n)->Vec4:
        return Vec4(self[n], self[n + 4], self[n + 8], self[n + 12])

    @property
    def lefttop3(self)->Mat3:
        return Mat3(self.m00, self.m01, self.m02,
                    self.m10, self.m11, self.m12,
                    self.m20, self.m21, self.m22)

    @property
    def transposed(self)->'Mat4':
        return Mat4(self.m00, self.m10, self.m20, self.m30,
                    self.m01, self.m11, self.m21, self.m31,
                    self.m02, self.m12, self.m22, self.m32,
                    self.m03, self.m13, self.m23, self.m33)

    def __mul__(self, rhs)->'Mat4':
        return Mat4(
            self.row(0).dot(rhs.col(0)),
            self.row(0).dot(rhs.col(1)),
            self.row(0).dot(rhs.col(2)),
            self.row(0).dot(rhs.col(3)),
            self.row(1).dot(rhs.col(0)),
            self.row(1).dot(rhs.col(1)),
            self.row(1).dot(rhs.col(2)),
            self.row(1).dot(rhs.col(3)),
            self.row(2).dot(rhs.col(0)),
            self.row(2).dot(rhs.col(1)),
            self.row(2).dot(rhs.col(2)),
            self.row(2).dot(rhs.col(3)),
            self.row(3).dot(rhs.col(0)),
            self.row(3).dot(rhs.col(1)),
            self.row(3).dot(rhs.col(2)),
            self.row(3).dot(rhs.col(3)))

    def apply4(self, v4: Vec4)->Vec4:
        return Vec4(v4.dot(self.col(0)),
                    v4.dot(self.col(1)),
                    v4.dot(self.col(2)),
                    v4.dot(self.col(3)))

    def apply3(self, v: Vec3)->Vec3:
        v4 = Vec4(v.x, v.y, v.z, 1)
        applied = Vec4(v4.dot(self.col(0)),
                       v4.dot(self.col(1)),
                       v4.dot(self.col(2)),
                       v4.dot(self.col(3)))
        return applied.vec3

    @staticmethod
    def identity():
        return Mat4(1, 0, 0, 0,
                    0, 1, 0, 0,
                    0, 0, 1, 0,
                    0, 0, 0, 1)

    @staticmethod
    def perspective(fovy, aspect, zNear, zFar):
        tan = math.atan(math.radians(fovy / 2))
        f = 1 / tan
        return Mat4(f / aspect, 0, 0, 0,
                    0, f, 0, 0,
                    0, 0, (zFar + zNear) / (zNear - zFar), -1,
                    0, 0, 2 * zFar * zNear / (zNear - zFar), 0)

    @staticmethod
    def translate(x, y, z):
        return Mat4(1, 0, 0, 0,
                    0, 1, 0, 0,
                    0, 0, 1, 0,
                    x, y, z, 1)


class _Transform(NamedTuple):
    pos: Vec3
    rot: Quaternion


class Transform(_Transform):
    @staticmethod
    def identity():
        return Transform(Vec3.zero(), Quaternion.identity())

    @property
    def mat4(self):
        r = self.rot.to_mat3()
        return Mat4(r.m00, r.m01, r.m02, 0,
                    r.m10, r.m11, r.m12, 0,
                    r.m20, r.m21, r.m22, 0,
                    self.pos.x, self.pos.y, self.pos.z, 1)

    def __mul__(self, rhs)->'Transform':
        pos = self.rot.to_mat3().apply(self.pos) + rhs.pos
        rot = self.rot * rhs.rot
        return Transform(pos, rot)


##############################################################################
# TestCases
##############################################################################
class Vec3TestCase(unittest.TestCase):
    def test_vec3(self):
        self.assertEqual(Vec3(0, 0, 0), Vec3())
        self.assertEqual(Vec3(0, 0, 0), Vec3.zero())
        self.assertEqual((0, 0, 0), Vec3.zero())
        self.assertEqual(Vec3(1, 1, 1), Vec3.one())
        self.assertEqual(Vec3(2, 2, 2), Vec3.one() + Vec3.one())


class Vec4TestCase(unittest.TestCase):
    def test_vec4(self):
        self.assertEqual(Vec4(0, 0, 0, 0), Vec4.zero())
        self.assertEqual((0, 0, 0, 0), Vec4.zero())
        self.assertEqual(Vec4(1, 1, 1, 1), Vec4.one())
        self.assertEqual(Vec4(2, 2, 2, 2), Vec4.one() + Vec4.one())


class QuaternionTestCase(unittest.TestCase):
    def test_quaternion4(self):
        self.assertEqual(Quaternion(0, 0, 0, 1), Quaternion.identity())
        self.assertEqual(Quaternion(0, 0, 0, 1), Quaternion.identity() * Quaternion.identity())
        self.assertEqual(Mat3.identity(), Quaternion.identity().to_mat3())


class Mat4TestCase(unittest.TestCase):

    def test_translate(self):
        p = Vec3.zero()
        m = Mat4.translate(1, 2, 3)
        pp = m.apply3(p)
        self.assertEqual(Vec3(1, 2, 3), pp)

    def test_matrix(self):
        a = Mat4.translate(1, 2, 3)
        b = Mat4.translate(2, 3, 4)
        c = a * b
        self.assertEqual(Mat4.translate(3, 5, 7), c)

        d = Mat4.translate(4, 5, 6)
        e = Mat4(*d)

        self.assertEqual(d, e)
        self.assertEqual(d.row(3), Vec4(4, 5, 6, 1))


class TransformTestCase(unittest.TestCase):

    def test_transform(self):
        a = Transform(Vec3(1, 2, 3), Quaternion.from_mat3(Mat3.rotation_y_axis_by_degree(90)))
        b = a * a
        self.assertEqual(Vec3(4, 4, 4), b.pos)


if __name__ == '__main__':
    unittest.main()
