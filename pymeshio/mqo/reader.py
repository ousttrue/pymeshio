# coding: utf-8
import io
import pymeshio.common
import pymeshio.mqo
"""
#print(sys.version_info[0])
        #if sys.version_info[0]<3:
        #    io=open(path, )
        #else:
        #    io=open(path, encoding='cp932')
        #result=method(self)
        #self.io.close()
        #self.io=None
        #return result
"""


class Reader(object):
    """mqo reader
    """
    __slots__=[
            "has_mikoto",
            "eof", "ios", "lines",
            "materials", "objects",
            ]
    def __init__(self, ios):
        self.ios=ios
        self.eof=False
        self.lines=0

    def __str__(self):
        return "<MQO %d lines, %d materials, %d objects>" % (
                self.lines, len(self.materials), len(self.objects))

    def getline(self):
        line=self.ios.readline()
        self.lines+=1
        if line=="":
            self.eof=True
            return None
        return line.strip()

    def printError(self, method, msg):
        print("%s:%s:%d" % (method, msg, self.lines))

    def readObject(self, name):
        obj=pymeshio.mqo.Obj(name)
        while(True):
            line=self.getline()
            if line==None:
                # eof
                break;
            if line=="":
                # empty line
                continue

            if line=="}":
                return obj
            else:
                tokens=line.split()
                key=tokens[0]
                if key=="vertex":
                    if not self.readVertex(obj):
                        return False
                elif key=="face":
                    if not self.readFace(obj):
                        return False
                elif key=="depth":
                    obj.depth=int(tokens[1])
                else:
                    print(
                            "%s#readObject" % name,
                            "unknown key: %s" % key
                            )

        self.printError("readObject", "invalid eof")
        return False

    def readFace(self, obj):
        while(True):
            line=self.getline()
            if line==None:
                # eof
                break;
            if line=="":
                # empty line
                continue

            if line=="}":
                return True
            else:
                # face
                tokens=line.split(' ', 1)
                try:
                    obj.addFace(pymeshio.mqo.Face(int(tokens[0]), tokens[1]))
                except ValueError as ex:
                    self.printError("readFace", ex)
                    #return False

        self.printError("readFace", "invalid eof")
        return False

    def readVertex(self, obj):
        while(True):
            line=self.getline()
            if line==None:
                # eof
                break;
            if line=="":
                # empty line
                continue

            if line=="}":
                return True
            else:
                # vertex
                obj.addVertex(*[float(v) for v in line.split()])

        self.printError("readVertex", "invalid eof")
        return False

    def readMaterial(self):
        materials=[]
        while(True):
            line=self.getline()
            if line==None:
                # eof
                break;
            if line=="":
                # empty line
                continue

            if line=="}":
                return materials
            else:
                # material
                secondQuaote=line.find('"', 1)                
                material=pymeshio.mqo.Material(line[1:secondQuaote])
                try:
                    material.parse(line[secondQuaote+2:])
                except ValueError as ex:
                    self.printError("readMaterial", ex)

                materials.append(material)

        self.printError("readMaterial", "invalid eof")
        return False

    def readChunk(self):
        level=1
        while(True):
            line=self.getline()
            if line==None:
                # eof
                break;
            if line=="":
                # empty line
                continue

            if line=="}":
                level-=1
                if level==0:
                    return True
            elif line.find("{")!=-1:
                level+=1

        self.printError("readChunk", "invalid eof")
        return False


def read_from_file(path):
    with io.open(path, 'rb') as ios:
        return read(ios)


def read(ios):
    print(type(ios), ios)
    assert(isinstance(ios, io.IOBase))
    reader=Reader(ios)
    model=pymeshio.mqo.Model()

    line=reader.getline()
    if line!="Metasequoia Document":
        print("invalid signature")
        return False

    line=reader.getline()
    if line!="Format Text Ver 1.0":
        print("unknown version: %s" % line)

    while True:
        line=reader.getline()
        if line==None:
            # eof
            break;
        if line=="":
            # empty line
            continue

        tokens=line.split()
        key=tokens[0]
        if key=="Eof":
            return model
        elif key=="Scene":
            if not reader.readChunk():
                return
        elif key=="Material":
            materials=reader.readMaterial()
            if not materials:
                return
            model.materials=materials
        elif key=="Object":
            firstQuote=line.find('"')
            secondQuote=line.find('"', firstQuote+1)
            obj=reader.readObject(line[firstQuote+1:secondQuote])
            if not obj:
                return
            model.objects.append(obj)
        elif key=="BackImage":
            if not reader.readChunk():
                return
        elif key=="IncludeXml":
            firstQuote=line.find('"')
            secondQuote=line.find('"', firstQuote+1)
            print("IncludeXml", line[firstQuote+1:secondQuote])
        else:
            print("unknown key: %s" % key)
            if not reader.readChunk():
                return
    # error not reach here
    raise ParseException("invalid eof")

