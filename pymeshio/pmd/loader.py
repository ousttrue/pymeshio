#coding: utf-8
import io
import pymeshio.common
import pymeshio.pmd


class Loader(pymeshio.common.BinaryLoader):
    """pmx loader
    """
    def __init__(self, io, version):
        super(Loader, self).__init__(io)
        self.version=version

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

    def read_vertex(self):
        return pymeshio.pmd.Vertex(
                self.read_vector3(),
                self.read_vector3(),
                self.read_vector2(),
                self.read_uint(2),
                self.read_uint(2),
                self.read_uint(1),
                self.read_uint(1))

    def read_material(self):
        return pymeshio.pmd.Material(
                diffuse_color=self.read_rgb(),
                alpha=self.read_float(),
                specular_factor=self.read_float(),
                specular_color=self.read_rgb(),
                ambient_color=self.read_rgb(),
                toon_index=self.read_uint(1),
                edge_flag=self.read_uint(1),
                vertex_count=self.read_uint(4),
                texture_file=self.read_text(20)
                )

    def read_bone(self):
        name=self.read_text(20)
        parent_index=self.read_uint(2)
        tail_index=self.read_uint(2)
        bone=pymeshio.pmd.createBone(name, self.read_uint(1))
        bone.parent_index=parent_index
        bone.tail_index=tail_index
        bone.ik_index = self.read_uint(2)
        bone.pos = self.read_vector3()
        return bone

    def read_ik(self):
        ik=pymeshio.pmd.IK(self.read_uint(2), self.read_uint(2))
        ik.length = self.read_uint(1)
        ik.iterations = self.read_uint(2)
        ik.weight = self.read_float()
        ik.children=[self.read_uint(2) for _ in range(ik.length)]
        return ik

    def read_morph(self):
        skin=pymeshio.pmd.Skin(self.read_text(20))
        skin_size = self.read_uint(4)
        skin.type = self.read_uint(1)
        for j in range(skin_size):
            skin.indices.append(self.read_uint(4))
            skin.pos_list.append(self.read_vector3())
        return skin

    def read_rigidbody(self):
        return pymeshio.pmd.RigidBody(
                name=self.read_text(20), 
                bone_index=self.read_uint(2),
                collision_group=self.read_uint(1),
                no_collision_group=self.read_uint(2),
                shape_type=self.read_uint(1),
                shape_size=self.read_vector3(),
                shape_position=self.read_vector3(),
                shape_rotation=self.read_vector3(),
                mass=self.read_float(),
                linear_damping=self.read_float(),
                angular_damping=self.read_float(),
                restitution=self.read_float(),
                friction=self.read_float(),
                mode=self.read_uint(1)
                )

    def read_joint(self):
        return pymeshio.pmd.Joint(
                name=self.read_text(20),
                rigidbody_index_a=self.read_uint(4),
                rigidbody_index_b=self.read_uint(4),
                position=self.read_vector3(),
                rotation=self.read_vector3(),
                translation_limit_min=self.read_vector3(),
                translation_limit_max=self.read_vector3(),
                rotation_limit_min=self.read_vector3(),
                rotation_limit_max=self.read_vector3(),
                spring_constant_translation=self.read_vector3(),
                spring_constant_rotation=self.read_vector3())



def __load(loader, model):
    # model info
    model.name=loader.read_text(20)
    model.comment=loader.read_text(256) 

    # model data
    model.vertices=[loader.read_vertex()
            for _ in range(loader.read_uint(4))]
    model.indices=[loader.read_uint(2)
            for _ in range(loader.read_uint(4))]
    model.materials=[loader.read_material()
            for _ in range(loader.read_uint(4))]
    model.bones=[loader.read_bone()
            for _ in range(loader.read_uint(2))]
    model.ik_list=[loader.read_ik()
            for _ in range(loader.read_uint(2))]
    model.morphs=[loader.read_morph()
            for _ in range(loader.read_uint(2))]
    model.morph_indices=[loader.read_uint(2)
            for _ in range(loader.read_uint(1))]
    model.bone_group_list=[loader.read_text(50)
            for _ in range(loader.read_uint(1))]
    model.bone_display_list=[(loader.read_uint(2), loader.read_uint(1))
            for _i in range(loader.read_uint(4))]

    if loader.is_end():
        # EOF
        return True

    ############################################################
    # extend1: english name
    ############################################################
    if loader.read_uint(1)==0:
        print("no extend flag")
        return True
    model.english_name=loader.read_text(20)
    model.english_comment=loader.read_text(256)
    for bone in model.bones:
        bone.english_name=loader.read_text(20)
    for morph in model.morphs:
        if morph.name==b'base':
            continue
        morph.english_name=loader.read_text(20)
    for bone_group in model.bone_group_list:
        bone_group=loader.read_text(50)

    ############################################################
    # extend2: toon_textures
    ############################################################
    if loader.is_end():
        # EOF
        return True
    model.toon_textures=[loader.read_text(100)
            for _ in range(10)]

    ############################################################
    # extend2: rigidbodies and joints
    ############################################################
    if loader.is_end():
        # EOF
        return True
    model.rigidbodies=[loader.read_rigidbody()
            for _ in range(loader.read_uint(4))]
    model.joints=[loader.read_joint()
            for _ in range(loader.read_uint(4))]

    return True


def load(path):
    # general binary loader
    #loader=pymeshio.common.BinaryLoader(open(path, 'rb'))
    loader=pymeshio.common.BinaryLoader(io.BytesIO(pymeshio.common.readall(path)))

    # header
    signature=loader.unpack("3s", 3)
    if signature!=b"Pmd":
        raise pymeshio.common.ParseException(
                "invalid signature: {0}".format(signature))
    version=loader.read_float()

    model=pymeshio.pmd.Model(version)
    loader=Loader(loader.io, version)
    if(__load(loader, model)):
        # check eof
        if not loader.is_end():
            print("can not reach eof.")

        # build bone tree
        for i, child in enumerate(model.bones):
            if child.parent_index==0xFFFF:
                # no parent
                model.no_parent_bones.append(child)
                child.parent=None
            else:
                # has parent
                parent=model.bones[child.parent_index]
                child.parent=parent
                parent.children.append(child)
            # ŒãˆÊ’u
            if child.hasChild():
                child.tail=model.bones[child.tail_index].pos

        return model


def save(self, path):
    io=open(path, 'wb')
    if not io:
        return False
    # Header
    io.write(b"Pmd")
    io.write(struct.pack("f", self.version))
    io.write(struct.pack("20s", self.name))
    io.write(struct.pack("256s", self.comment))

    # Vertices
    io.write(struct.pack("I", len(self.vertices)))
    sVertex=struct.Struct("=8f2H2B") # 38byte
    assert(sVertex.size==38)
    for v in self.vertices:
        data=sVertex.pack( 
            v.pos[0], v.pos[1], v.pos[2],
            v.normal[0], v.normal[1], v.normal[2],
            v.uv[0], v.uv[1],
            v.bone0, v.bone1, v.weight0, v.edge_flag)
        io.write(data)

    # Faces
    io.write(struct.pack("I", len(self.indices)))
    io.write(struct.pack("=%dH" % len(self.indices), *self.indices))

    # material
    io.write(struct.pack("I", len(self.materials)))
    sMaterial=struct.Struct("=3fff3f3fBBI20s") # 70byte
    assert(sMaterial.size==70)
    for m in self.materials:
        io.write(sMaterial.pack(
            m.diffuse[0], m.diffuse[1], m.diffuse[2], m.diffuse[3],
            m.shinness, 
            m.specular[0], m.specular[1], m.specular[2],
            m.ambient[0], m.ambient[1], m.ambient[2],
            m.toon_index, m.flag,
            m.vertex_count,
            m.texture
            ))

    # bone
    io.write(struct.pack("H", len(self.bones)))
    sBone=struct.Struct("=20sHHBH3f")
    assert(sBone.size==39)
    for b in self.bones:
        io.write(sBone.pack(
            b.name,
            b.parent_index, b.tail_index, b.type, b.ik_index,
            b.pos[0], b.pos[1], b.pos[2]))

    # IK
    io.write(struct.pack("H", len(self.ik_list)))
    for ik in self.ik_list:
        io.write(struct.pack("=2HBHf", 
            ik.index, ik.target, ik.length, ik.iterations, ik.weight
            ))
        for c in ik.children:
            io.write(struct.pack("H", c))

    # skin
    io.write(struct.pack("H", len(self.morph_list)))
    for s in self.morph_list:
        io.write(struct.pack("20sIB", 
            s.name, len(s.indices), s.type))
        for i, v in zip(s.indices, s.pos_list):
            io.write(struct.pack("I3f", i, v[0], v[1], v[2]))

    # skin disp list
    io.write(struct.pack("B", len(self.face_list)))
    for i in self.face_list:
        io.write(struct.pack("H", i))

    # bone disp list
    io.write(struct.pack("B", len(self.bone_group_list)))
    for g in self.bone_group_list:
        io.write(struct.pack("50s", g.name))

    io.write(struct.pack("I", len(self.bone_display_list)))
    for l in self.bone_display_list:
        io.write(struct.pack("=HB", *l))

    ############################################################
    # extend data
    ############################################################
    io.write(struct.pack("B", 1))
    # english name
    io.write(struct.pack("=20s", self.english_name))
    io.write(struct.pack("=256s", self.english_comment))
    # english bone name
    for bone in self.bones:
        io.write(struct.pack("=20s", bone.english_name))
    # english skin list
    for skin in self.morph_list:
        #print(skin.name)
        if skin.name==b'base':
            continue
        io.write(struct.pack("=20s", skin.english_name))
    # english bone list
    for bone_group in self.bone_group_list:
        io.write(struct.pack("50s", bone_group.english_name))
    # toon texture
    for toon_texture in self.toon_textures:
        io.write(struct.pack("=100s", toon_texture))
    # rigid
    io.write(struct.pack("I", len(self.rigidbodies)))
    for r in self.rigidbodies:
        io.write(struct.pack("=20sHBHB14fB",
            r.name, r.boneIndex, r.group, r.target, r.shapeType,
            r.w, r.h, r.d, 
            r.position.x, r.position.y, r.position.z, 
            r.rotation.x, r.rotation.y, r.rotation.z, 
            r.weight,
            r.linearDamping, r.angularDamping, r.restitution,
            r.friction, r.processType))

    # constraint
    io.write(struct.pack("I", len(self.constraints)))
    for c in self.constraints:
        io.write(struct.pack("=20sII24f",
            c.name, c.rigidA, c.rigidB,
            c.pos.x, c.pos.y, c.pos.z,
            c.rot.x, c.rot.y, c.rot.z,
            c.constraintPosMin.x, c.constraintPosMin.y, c.constraintPosMin.z,
            c.constraintPosMax.x, c.constraintPosMax.y, c.constraintPosMax.z,
            c.constraintRotMin.x, c.constraintRotMin.y, c.constraintRotMin.z,
            c.constraintRotMax.x, c.constraintRotMax.y, c.constraintRotMax.z,
            c.springPos.x, c.springPos.y, c.springPos.z,
            c.springRot.x, c.springRot.y, c.springRot.z
            ))

    return True

