from pymeshio.pmx import *
#self.__pos=self.__io.tell()



class Loader(object):
    """pmx loader

    Attributes:
        text_encoding: 
        extended_uv:
        vertex_index_size:
        texture_index_size:
        material_index_size:
        bone_index_size:
        morph_index_size:
        rigidbody_index_size:
    """
    def __init__(self, loader):
        self.__io=loader

    def __str__(self) -> str:
        return '<PmxIO>'

    def unpack(self, fmt: str, size: int) -> "read value as format":
        result=struct.unpack(fmt, self.__io.read(size))
        return result[0]

    def get_read_text(self) -> "text process function":
        if self.text_encoding==0:
            def read_text():
                size=self.read_uint(4)
                return self.unpack("{0}s".format(size), size).decode("UTF16")
            return read_text
        elif self.text_encoding==1:
            def read_text():
                size=self.read_uint(4)
                return self.unpack("{0}s".format(size), size).decode("UTF8")
            return read_text
        else:
            print("unknown text encoding", self.text_encoding)

    def read_uint(self, size):
        if size==1:
            return self.unpack("B", size)
        if size==2:
            return self.unpack("H", size)
        if size==4:
            return self.unpack("I", size)
        print("not reach here")
        raise ParseException("invalid int size: "+size)

    def read_float(self):
        return self.unpack("f", 4)

    def read_vector2(self):
        return common.Vector2(
                self.read_float(), 
                self.read_float()
                )

    def read_vector3(self):
        return common.Vector3(
                self.read_float(), 
                self.read_float(), 
                self.read_float()
                )

    def read_rgba(self):
        return common.RGBA(
                self.read_float(), 
                self.read_float(), 
                self.read_float(),
                self.read_float()
                )

    def read_rgb(self):
        return common.RGB(
                self.read_float(), 
                self.read_float(), 
                self.read_float()
                )

    def read_vertex(self):
        return Vertex(
                self.read_vector3(), # pos
                self.read_vector3(), # normal
                self.read_vector2(), # uv
                self.read_deform(), # deform(bone weight)
                self.read_float() # edge factor
                )

    def read_deform(self):
        deform_type=self.read_uint(1)
        if deform_type==0:
            return Bdef1(self.read_uint(self.bone_index_size))
        if deform_type==1:
            return Bdef2(
                    self.read_uint(self.bone_index_size),
                    self.read_uint(self.bone_index_size),
                    self.read_float()
                    )
        """
        if deform_type==2:
            return Bdef4(
                    self.read_uint(self.bone_index_size),
                    self.read_uint(self.bone_index_size),
                    self.read_uint(self.bone_index_size),
                    self.read_uint(self.bone_index_size),
                    self.read_float(), self.read_float(),
                    self.read_float(), self.read_float()
                    )
        """
        raise ParseException("unknown deform type: {0}".format(deform_type))

    def read_material(self):
        material=Material(
                name=self.read_text(),
                english_name=self.read_text(),
                diffuse_color=self.read_rgb(),
                diffuse_alpha=self.read_float(),
                specular_color=self.read_rgb(),
                specular_factor=self.read_float(),
                ambient_color=self.read_rgb(),
                flag=self.read_uint(1),
                edge_color=self.read_rgba(),
                edge_size=self.read_float(),
                texture_index=self.read_uint(self.texture_index_size),
                sphia_texture_index=self.read_uint(self.texture_index_size),
                sphia_mode=self.read_uint(1),
                toon_sharing_flag=self.read_uint(1),
                )
        if material.toon_sharing_flag==0:
            material.toon_texture_index=self.read_uint(self.texture_index_size)
        elif material.toon_sharing_flag==1:
            material.toon_texture_index=self.read_uint(1)
        else:
            raise ParseException("unknown toon_sharing_flag {0}".format(material.toon_sharing_flag))
        material.comment=self.read_text()
        material.index_count=self.read_uint(4)
        return material

    def read_bone(self):
        bone=Bone(
                name=self.read_text(),
                english_name=self.read_text(),
                position=self.read_vector3(),
                parent_index=self.read_uint(self.bone_index_size),
                layer=self.read_uint(4),
                flag=self.read_uint(2)                
                )
        if bone.getConnectionFlag()==0:
            bone.tail_positoin=self.read_vector3()
        elif bone.getConnectionFlag()==1:
            bone.tail_index=self.read_uint(self.bone_index_size)
        else:
            raise ParseException("unknown bone conenction flag: {0}".format(
                bone.getConnectionFlag()))

        if bone.getRotationFlag()==1 or bone.getTranslationFlag()==1:
            bone.effect_index=self.read_uint(self.bone_index_size)
            bone.effect_factor=self.read_float()

        if bone.getFixedAxisFlag()==1:
            bone.fixed_axis=self.read_vector3()

        if bone.getLocalCoordinateFlag()==1:
            bone.local_x_vector=self.read_vector3()
            bone.local_z_vector=self.read_vector3()

        if bone.getExternalParentDeformFlag()==1:
            bone.external_key=self.read_uint(4)

        if bone.getIkFlag()==1:
            bone.ik=self.read_ik()

        return bone

    def read_ik(self):
        ik=Ik(
                target_index=self.read_uint(self.bone_index_size),
                loop=self.read_uint(4),
                limit_radian=self.read_float())
        link_size=self.read_uint(4)
        ik.link=[self.read_ik_link() for i in range(link_size)]

    def read_ik_link(self):
        link=IkLink(
                self.read_uint(self.bone_index_size),
                self.read_uint(1))
        if link.limit_angle==0:
            pass
        elif link.limit_angle==1:
            link.limit_min=self.read_vector3()
            link.limit_max=self.read_vector3()
        else:
            raise ParseException("invalid ik link limit_angle: {0}".format(
                link.limit_angle))
        return link


def load(path: str) -> Model:
    with open(path, "rb") as f:
        model=Model()
        loader=Loader(f)

        ####################
        # header
        ####################
        signature=loader.unpack("4s", 4)
        if signature!=b"PMX ":
            raise ParseException("invalid signature", loader.signature)

        version=loader.read_float()
        if version!=2.0:
            print("unknown version", version)

        model.version=version
        # flags
        flag_bytes=loader.read_uint(1)
        if flag_bytes!=8:
            raise ParseException("invalid flag length", loader.flag_bytes)

        # text encoding
        loader.text_encoding=loader.read_uint(1)
        loader.read_text=loader.get_read_text()
        # uv
        loader.extended_uv=loader.read_uint(1)
        if loader.extended_uv>0:
            raise ParseException("extended uv is not supported", loader.extended_uv)

        # index size
        loader.vertex_index_size=loader.read_uint(1)
        loader.texture_index_size=loader.read_uint(1)
        loader.material_index_size=loader.read_uint(1)
        loader.bone_index_size=loader.read_uint(1)
        loader.morph_index_size=loader.read_uint(1)
        loader.rigidbody_index_size=loader.read_uint(1)

        ####################
        # model info
        ####################
        model.name = loader.read_text()
        model.english_name = loader.read_text()
        model.comment = loader.read_text()
        model.english_comment = loader.read_text()

        ####################
        # vertices
        ####################
        vertex_count=loader.read_uint(4)
        model.vertices=[loader.read_vertex() 
                for i in range(vertex_count)]

        ####################
        # indices
        ####################
        index_count=loader.read_uint(4)
        model.indices=[loader.read_uint(loader.vertex_index_size) 
                for i in range(index_count)]

        ####################
        # textures
        ####################
        texture_count=loader.read_uint(4)
        model.textures=[loader.read_text() 
                for i in range(texture_count)]

        ####################
        # materials
        ####################
        material_count=loader.read_uint(4)
        model.materials=[loader.read_material() 
                for i in range(material_count)]

        ####################
        # bones
        ####################
        bone_count=loader.read_uint(4)
        model.bones=[loader.read_bone() 
                for i in range(bone_count)]
        return model

