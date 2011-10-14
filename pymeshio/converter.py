# coding: utf-8
"""
convert model
"""

import math
from . import common
from .common import unicode as u
from . import pmx
from . import pmd

class ConvertException(Exception):
    """
    Exception in writer
    """
    pass


def pmd_to_pmx(src):
    """
    return pymeshio.pmx.Model.

    :Parameters:
        src
            pymeshio.pmd.Model
    """
    dst=pmx.Model()
    # model info
    dst.name=src.name.decode("cp932")
    dst.english_name=src.english_name.decode("cp932")
    dst.comment=src.comment.replace(
            b"\n", b"\r\n").decode("cp932")
    dst.english_comment=src.english_comment.replace(
            b"\n", b"\r\n").decode("cp932")
    # vertices
    def createDeform(bone0, bone1, weight0):
        if weight0==0:
            return pmx.Bdef1(bone1)
        elif weight0==100:
            return pmx.Bdef1(bone0)
        else:
            return pmx.Bdef2(bone0, bone1, weight0*0.01)
    dst.vertices=[
            pmx.Vertex(
                v.pos, 
                v.normal, 
                v.uv, 
                createDeform(v.bone0, v.bone1, v.weight0), 
                1.0 if v.edge_flag==0 else 0.0
                )
            for v in src.vertices]
    # indices
    dst.indices=src.indices[:]
    # materials
    texture_map={}
    def get_flag(m):
        return (
                (1 if False  else 0)+
                (2 if (m.edge_flag & 1!=0) else 0)+
                (4 if True else 0)+
                (8 if True else 0)+
                (16 if (m.edge_flag & 1!=0) else 0)
                )
    def get_texture_file(path):
        if len(path)==0:
            return None
        elif path.find(b'*')==-1:
            return path
        else:
            return b'*'.split(path)[0]
    def get_sphere_texture_file(path):
        if len(path)==0:
            return None
        elif path.find(b'*')==-1:
            return None
        else:
            return b'*'.split(path)[1]
    def get_texture_index(path):
        try:
            return texture_map[get_texture_file(path)]
        except KeyError:
            return -1
    def get_sphere_texture_index(path):
        try:
            return texture_map[get_sphere_texture_file(path)]
        except KeyError:
            return -1
    def get_sphere_texture_flag(path):
        sphere_texture=get_sphere_texture_file(path)
        if sphere_texture:
            if sphere_texture.endswith('.sph'):
                return 1
            elif sphere_texture.endswith('.spa'):
                return 2
            else:
                raise ConvertException(
                        "invalid sphere texture: {0}".format(sphere_texture))
        return 0
    def get_toon_shared_flag(m):
        return 1
    def get_toon_index(m):
        return m.toon_index
    for m in src.materials:
        texture=get_texture_file(m.texture_file)
        if texture and not texture in texture_map:
            texture_map[texture]=len(texture_map)
            dst.textures.append(texture.decode("cp932"))
        sphere_texture=get_sphere_texture_file(m.texture_file)
        if sphere_texture and not sphere_texture in texture_map:
            texture_map[sphere_texture]=len(texture_map)
            dst.textures.append(sphere_texture.decode("cp932"))
    dst.materials=[
            pmx.Material(
                name=common.unicode(""),
                english_name=common.unicode(""),
                diffuse_color=m.diffuse_color,
                alpha=m.alpha,
                specular_factor=m.specular_factor,
                specular_color=m.specular_color,
                ambient_color=m.ambient_color,
                flag=get_flag(m),
                edge_color=common.RGBA(0.0, 0.0, 0.0, 1.0),
                edge_size=1.0,
                texture_index=get_texture_index(m.texture_file),
                sphere_texture_index=get_sphere_texture_index(m.texture_file),
                sphere_mode=get_sphere_texture_flag(m.texture_file),
                toon_sharing_flag=get_toon_shared_flag(m),
                toon_texture_index=get_toon_index(m),
                comment=common.unicode(""),
                vertex_count=m.vertex_count
                )
            for i, m in enumerate(src.materials)]
    # bones
    ik_map={}
    for ik in src.ik_list:
        ik_map[ik.index]=ik
    def is_connected(b):
        if isinstance(b, pmd.Bone_Rolling):
            return False
        if isinstance(b, pmd.Bone_Tweak):
            return False
        return True
    def is_rotatable(b):
        if isinstance(b, pmd.Bone_Rotate):
            return True
        if isinstance(b, pmd.Bone_RotateMove):
            return True
        if isinstance(b, pmd.Bone_RotateInfl):
            return True
        if isinstance(b, pmd.Bone_IKRotateInfl):
            return True
        if isinstance(b, pmd.Bone_Rolling):
            return True
        if isinstance(b, pmd.Bone_IKTarget):
            return True
        if isinstance(b, pmd.Bone_IK):
            return True
        if isinstance(b, pmd.Bone_Unvisible):
            return True
        if isinstance(b, pmd.Bone_Tweak):
            return True
    def is_movable(b):
        if isinstance(b, pmd.Bone_RotateMove):
            return True
        if isinstance(b, pmd.Bone_IK):
            return True
    def is_visible(b):
        if isinstance(b, pmd.Bone_Unvisible):
            return False
        if isinstance(b, pmd.Bone_IKTarget):
            return False
        if isinstance(b, pmd.Bone_Tweak):
            return False
        return True
    def is_manupilatable(b):
        return True
    def has_ik(b):
        if isinstance(b, pmd.Bone_IK):
            return True
    def is_external_rotation(b):
        if isinstance(b, pmd.Bone_RotateInfl):
            return True
        if isinstance(b, pmd.Bone_Tweak):
            return True
    def is_fixed_axis(b):
        if isinstance(b, pmd.Bone_Rolling):
            return True
    def is_local_axis(b):
        pass
    def after_physics(b):
        pass
    def external_parent(b):
        pass
    def get_bone_flag(b):
        return (
                (1 if is_connected(b) else 0)+
                (2 if is_rotatable(b) else 0)+
                (4 if is_movable(b) else 0)+
                (8 if is_visible(b) else 0)+

                (16 if is_manupilatable(b) else 0)+
                (32 if has_ik(b) else 0)+
                0+
                0+

                (256 if is_external_rotation(b) else 0)+
                0+
                (1024 if is_fixed_axis(b) else 0)+
                (2048 if is_local_axis(b) else 0)+

                (4096 if after_physics(b) else 0)+
                (8192 if external_parent(b) else 0)
                )
    def get_tail_position(b):
        return common.Vector3()
    def get_tail_index(b):
        if isinstance(b, pmd.Bone_Rolling):
            return -1
        if isinstance(b, pmd.Bone_IKTarget):
            return -1
        if isinstance(b, pmd.Bone_Unvisible):
            return -1
        if isinstance(b, pmd.Bone_Tweak):
            return -1
        return b.tail_index
    def get_ik_link(bone_index):
        b=src.bones[bone_index]
        if b.english_name.find(b'knee')==-1:
            return pmx.IkLink(
                            bone_index, 0, 
                            common.Vector3(), 
                            common.Vector3())
        else:
            return pmx.IkLink(
                            bone_index, 1, 
                            common.Vector3(-3.1415927410125732, 0.0, 0.0), 
                            common.Vector3(-0.00872664619237184524536132812500, 0.0, 0.0))
    def get_ik(b):
        if isinstance(b, pmd.Bone_IK):
            ik=ik_map[b.index]
            return pmx.Ik(
                    ik.target, ik.iterations, ik.weight * 4, [
                        get_ik_link(child) for child in ik.children ])
        return None
    def get_layer(b):
        return 0
    dst.bones=[
            pmx.Bone(
                name=b.name.decode('cp932'),
                english_name=b.english_name.decode('cp932'),
                position=b.pos,
                parent_index=b.parent_index if b.parent_index!=65535 else -1,
                layer=get_layer(b),
                flag=get_bone_flag(b),
                tail_position=get_tail_position(b),
                tail_index=get_tail_index(b),
                effect_index=-1,
                effect_factor=0.0,
                fixed_axis=common.Vector3(),
                local_x_vector=common.Vector3(),
                local_z_vector=common.Vector3(),
                external_key=-1,
                ik=get_ik(b),
                )
            for i, b in enumerate(src.bones)]
    # bones
    def get_panel(m):
        return 1
    if len(src.morphs)>0:
        base=src.morphs[0]
        assert(base.name==b"base")
        dst.morphs=[
                pmx.Morph(
                    name=m.name.decode('cp932'),
                    english_name=m.english_name.decode('cp932'),
                    panel=get_panel(m),
                    morph_type=1,
                    offsets=[pmx.VertexMorphOffset(base.indices[i], pos)
                        for i, pos in zip(m.indices, m.pos_list)]
                    )
                for i, m in enumerate(src.morphs) if m.name!=b"base"]
    # display_slots
    dst.display_slots=[
            pmx.DisplaySlot(u('Root'), u('Root'), 1),
            pmx.DisplaySlot(u('表情'), u('Exp'), 1)]+[
                    pmx.DisplaySlot(
                        name=g.name.strip().decode('cp932'),
                        english_name=g.english_name.strip().decode('cp932'),
                        special_flag=0)
                    for i, g in enumerate(src.bone_group_list)]
    # rigidbodies
    dst.rigidbodies=[
            pmx.RigidBody(
                name=r.name.decode("cp932"),
                english_name=u(""),
                bone_index=r.bone_index,
                collision_group=r.collision_group,
                no_collision_group=r.no_collision_group,
                shape_type=r.shape_type,
                shape_size=r.shape_size,
                shape_position=r.shape_position,
                shape_rotation=r.shape_rotation,
                mass=r.mass,
                linear_damping=r.linear_damping,
                angular_damping=r.angular_damping,
                restitution=r.restitution,
                friction=r.friction,
                mode=r.mode
                )
            for i, r in enumerate(src.rigidbodies)]
    # joints
    dst.joints=[
            pmx.Joint(
                j.name.decode('cp932'),
                u(""),
                0,
                j.rigidbody_index_a,
                j.rigidbody_index_b,
                j.position,
                j.rotation,
                j.translation_limit_min,
                j.translation_limit_max,
                j.rotation_limit_min,
                j.rotation_limit_max,
                j.spring_constant_translation,
                j.spring_constant_rotation
                )
            for i, j in enumerate(src.joints)]
    return dst

