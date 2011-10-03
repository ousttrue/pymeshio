# coding: utf-8
import io
import struct
from .. import common
from .. import pmx

class Writer(common.BinaryWriter):
    """pmx writer
    """
    def __init__(self, ios,
            text_encoding, extended_uv,
            vertex_index_size, texture_index_size, material_index_size,
            bone_index_size, morph_index_size, rigidbody_index_size):
        super(Writer, self).__init__(ios)
        if text_encoding==0:
            def write_text(unicode):
               utf16=unicode.encode('utf16') 
               self.write_uint(len(utf16), 4)
               self.write_bytes(utf16)
            self.write_text=write_text
        elif text_encoding==1:
            def write_text(unicode):
               utf8=unicode.encode('utf8') 
               self.write_uint(len(utf8), 4)
               self.write_bytes(utf8)
            self.write_text=write_text
        else:
            raise WriteError(
                    "invalid text_encoding: {0}".format(text_encoding))

        self.write_vertex_index=lambda index: self.write_uint(index, vertex_index_size)
        self.write_texture_index=lambda index: self.write_uint(index, texture_index_size)
        self.write_material_index=lambda index: self.write_uint(index, material_index_size)
        self.write_bone_index=lambda index: self.write_uint(index, bone_index_size)
        self.write_morph_index=lambda index: self.write_uint(index, morph_index_size)
        self.write_rigidbody_index=lambda index: self.write_uint(index, rigidbody_index_size)

    def write_vertices(self, vertices):
        self.write_uint(len(vertices), 4)
        for v in vertices:
            self.write_vector3(v.position)
            self.write_vector3(v.normal)
            self.write_vector2(v.uv)
            self.write_deform(v.deform)
            self.write_float(v.edge_factor)

    def write_deform(self, deform):
        if isinstance(deform, pmx.Bdef1):
            self.write_uint(0, 1)
            self.write_bone_index(deform.index0)
        elif isinstance(deform, pmx.Bdef2):
            self.write_uint(1, 1)
            self.write_bone_index(deform.index0)
            self.write_bone_index(deform.index1)
            self.write_float(deform.weight0)
        elif isinstance(deform, pmx.Bdef4):
            # todo
            raise pymeshio.common.WriteException(
                    "not implemented Bdef4")
        else:
            raise pymeshio.common.WriteException(
                    "unknown deform type: {0}".format(deform.type))

    def write_indices(self, indices):
        self.write_uint(len(indices), 4)
        for i in indices:
            self.write_vertex_index(i)

    def write_textures(self, textures):
        self.write_uint(len(textures), 4)
        for t in textures:
            self.write_text(t)

    def write_materials(self, materials):
        self.write_uint(len(materials), 4)
        for m in materials:
            self.write_text(m.name)
            self.write_text(m.english_name)
            self.write_rgb(m.diffuse_color)
            self.write_float(m.alpha)
            self.write_rgb(m.specular_color)
            self.write_float(m.specular_factor)
            self.write_rgb(m.ambient_color)
            self.write_uint(m.flag, 1)
            self.write_rgba(m.edge_color)
            self.write_float(m.edge_size)
            self.write_texture_index(m.texture_index)
            self.write_texture_index(m.sphere_texture_index)
            self.write_uint(m.sphere_mode, 1)
            self.write_uint(m.toon_sharing_flag, 1)
            if m.toon_sharing_flag==0:
                self.write_texture_index(m.toon_texture_index)
            elif m.toon_sharing_flag==1:
                self.write_uint(m.toon_texture_index, 1)
            else:
                raise common.WriteException(
                        "unknown toon_sharing_flag {0}".format(m.toon_sharing_flag))
            self.write_text(m.comment)
            self.write_uint(m.vertex_count, 4)

    def write_bones(self, bones):
        self.write_uint(len(bones), 4)
        for bone in bones:
            self.write_text(bone.name)
            self.write_text(bone.english_name)
            self.write_vector3(bone.position)
            self.write_bone_index(bone.parent_index)
            self.write_uint(bone.layer, 4)
            self.write_uint(bone.flag, 2)
            if bone.getConnectionFlag()==0:
                self.write_vector3(bone.tail_positoin)
            elif bone.getConnectionFlag()==1:
                self.write_bone_index(bone.tail_index)
            else:
                raise pymeshio.common.WriteException(
                        "unknown bone conenction flag: {0}".format(
                            bone.getConnectionFlag()))

            if bone.getRotationFlag()==1 or bone.getTranslationFlag()==1:
                self.write_bone_index(bone.effect_index)
                self.write_float(bone.effect_factor)

            if bone.getFixedAxisFlag()==1:
                self.write_vector3(bone.fixed_axis)

            if bone.getLocalCoordinateFlag()==1:
                self.write_vector3(bone.local_x_vector)
                self.write_vector3(bone.local_z_vector)

            if bone.getExternalParentDeformFlag()==1:
                self.write_uint(bone.external_key, 4)

            if bone.getIkFlag()==1:
                self.write_ik(bone.ik)

    def write_ik(self, ik):
        self.write_bone_index(ik.target_index)
        self.write_uint(ik.loop, 4)
        self.write_float(ik.limit_radian)
        self.write_uint(len(ik.link), 4)
        for l in ik.link:
            self.write_ik_link(l)

    def write_ik_link(self, link):
        self.write_bone_index(link.bone_index)
        self.write_uint(link.limit_angle, 1)
        if link.limit_angle==0:
            pass
        elif link.limit_angle==1:
            self.write_vector3(link.limit_min)
            self.write_vector3(link.limit_max)
        else:
            raise pymeshio.common.WriteException(
                    "invalid ik link limit_angle: {0}".format(
                        link.limit_angle))
 
    def write_morph(self, morphs):
        self.write_uint(len(morphs), 4)
        for m in morphs:
            self.write_text(m.name)
            self.write_text(m.english_name)
            self.write_uint(m.panel, 1)
            self.write_uint(m.morph_type, 1)
            if m.morph_type==0:
                # todo
                raise pymeshio.common.WriteException(
                        "not implemented GroupMorph")
            elif m.morph_type==1:
                self.write_uint(len(m.offsets), 4)
                for o in m.offsets:
                    self.write_vertex_index(o.vertex_index)
                    self.write_vector3(o.position_offset)
            elif m.morph_type==2:
                # todo
                raise pymeshio.common.WriteException(
                        "not implemented BoneMorph")
            elif m.morph_type==3:
                # todo
                raise pymeshio.common.WriteException(
                        "not implemented UvMorph")
            elif m.morph_type==4:
                # todo
                raise pymeshio.common.WriteException(
                        "not implemented extended UvMorph1")
            elif m.morph_type==5:
                # todo
                raise pymeshio.common.WriteException(
                        "not implemented extended UvMorph2")
            elif m.morph_type==6:
                # todo
                raise pymeshio.common.WriteException(
                        "not implemented extended UvMorph3")
            elif m.morph_type==7:
                # todo
                raise pymeshio.common.WriteException(
                        "not implemented extended UvMorph4")
            elif m.morph_type==8:
                # todo
                raise pymeshio.common.WriteException(
                        "not implemented extended MaterialMorph")
            else:
                raise pymeshio.common.WriteException(
                        "unknown morph type: {0}".format(m.morph_type))

    def write_display_slots(self, display_slots):
        self.write_uint(len(display_slots), 4)
        for s in display_slots:
            self.write_text(s.name)
            self.write_text(s.english_name)
            self.write_uint(s.special_flag, 1)
            self.write_uint(len(s.refrences), 4)
            for r in s.refrences:
                self.write_uint(r[0], 1)
                if r[0]==0:
                    self.write_bone_index(r[1])
                elif r[0]==1:
                    self.write_morph_index(r[1])
                else:
                    raise pymeshio.common.WriteException(
                            "unknown display_type: {0}".format(r[0]))

    def write_rigidbodies(self, rigidbodies):
        self.write_uint(len(rigidbodies), 4)
        for rb in rigidbodies:
            self.write_text(rb.name)
            self.write_text(rb.english_name)
            self.write_bone_index(rb.bone_index)
            self.write_uint(rb.collision_group, 1)
            self.write_uint(rb.no_collision_group, 2)
            self.write_uint(rb.shape_type, 1)
            self.write_vector3(rb.shape_size)
            self.write_vector3(rb.shape_position)
            self.write_vector3(rb.shape_rotation)
            self.write_float(rb.param.mass)
            self.write_float(rb.param.linear_damping)
            self.write_float(rb.param.angular_damping)
            self.write_float(rb.param.restitution)
            self.write_float(rb.param.friction)
            self.write_uint(rb.mode, 1)

    def write_joints(self, joints):
        self.write_uint(len(joints), 4)
        for j in joints:
            self.write_text(j.name)
            self.write_text(j.english_name)
            self.write_uint(j.joint_type, 1)
            self.write_rigidbody_index(j.rigidbody_index_a)
            self.write_rigidbody_index(j.rigidbody_index_b)
            self.write_vector3(j.position)
            self.write_vector3(j.rotation)
            self.write_vector3(j.translation_limit_min)
            self.write_vector3(j.translation_limit_max)
            self.write_vector3(j.rotation_limit_min)
            self.write_vector3(j.rotation_limit_max)
            self.write_vector3(j.spring_constant_translation)
            self.write_vector3(j.spring_constant_rotation)


def write(ios, model, text_encoding=1):
    """pmxèëÇ´çûÇ›
    """
    assert(isinstance(ios, io.IOBase))
    assert(isinstance(model, pmx.Model))
    writer=common.BinaryWriter(ios)
    # header
    writer.write_bytes(b"PMX ")
    writer.write_float(model.version)

    # flags
    writer.write_uint(8, 1)
    # textencoding
    writer.write_uint(text_encoding, 1)
    # extend uv
    writer.write_uint(0, 1)
    def get_array_size(size):
        if size<128:
            return 1
        elif size<32768:
            return 2
        elif size<2147483647:
            return 4
        else:
            raise common.WriteError(
                    "invalid array_size: {0}".format(size))
    # vertex_index_size
    vertex_index_size=get_array_size(len(model.vertices))
    writer.write_uint(vertex_index_size, 1)
    # texture_index_size
    texture_index_size=get_array_size(len(model.textures))
    writer.write_uint(texture_index_size, 1)
    # material_index_size
    material_index_size=get_array_size(len(model.materials))
    writer.write_uint(material_index_size, 1)
    # bone_index_size
    bone_index_size=get_array_size(len(model.bones))
    writer.write_uint(bone_index_size, 1)
    # morph_index_size
    morph_index_size=get_array_size(len(model.morphs))
    writer.write_uint(morph_index_size, 1)
    # rigidbody_index_size
    rigidbody_index_size=get_array_size(len(model.rigidbodies))
    writer.write_uint(rigidbody_index_size, 1)

    writer=Writer(writer.ios, 
            text_encoding, 0,
            vertex_index_size, texture_index_size, material_index_size,
            bone_index_size, morph_index_size, rigidbody_index_size)
 
    # model info
    writer.write_text(model.name)
    writer.write_text(model.english_name)
    writer.write_text(model.comment)
    writer.write_text(model.english_comment)

    # model data
    writer.write_vertices(model.vertices)
    writer.write_indices(model.indices)
    writer.write_textures(model.textures)
    writer.write_materials(model.materials)
    writer.write_bones(model.bones)
    writer.write_morph(model.morphs)
    writer.write_display_slots(model.display_slots)
    writer.write_rigidbodies(model.rigidbodies)
    writer.write_joints(model.joints)
    return True

