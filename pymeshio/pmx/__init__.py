#!/usr/bin/env python
# coding: utf-8
"""
========================
MikuMikuDance PMX format
========================

file format
~~~~~~~~~~~
* PMDEditor's Lib/PMX仕様/PMX仕様.txt

specs
~~~~~
* textencoding: unicode
* coordinate: left handed y-up(DirectX)
* uv origin: 
* face: only triangle
* backculling: 

"""
__author__="ousttrue"
__license__="zlib"
__versioon__="1.0.0"


import io
import os
import struct
from pymeshio import common



class Ik(object):
    """ik info
    """
    __slots__=[
            'target_index',
            'loop',
            'limit_radian',
            'link',
            ]
    def __init__(self, target_index, loop, limit_radian):
        self.target_index=target_index
        self.loop=loop
        self.limit_radian=limit_radian
        self.link=[]


class IkLink(object):
    """ik link info
    """
    __slots__=[
            'bone_index',
            'limit_angle',
            'limit_min',
            'limit_max',
            ]
    def __init__(self, bone_index, limit_angle):
        self.bone_index=bone_index
        self.limit_angle=limit_angle
        self.limit_min=None
        self.limit_max=None


class Bone(object):
    """material

    Bone: see __init__
    """
    __slots__=[
            'name',
            'english_name',
            'position',
            'parent_index',
            'layer',
            'flag',

            'tail_positoin',
            'tail_index',
            'effect_index',
            'effect_factor',
            'fixed_axis',
            'local_x_vector',
            'local_z_vector',
            'external_key',
            'ik',
            ]
    def __init__(self,
            name,
            english_name,
            position,
            parent_index,
            layer,
            flag
            ):
        self.name=name
        self.english_name=english_name
        self.position=position
        self.parent_index=parent_index
        self.layer=layer
        self.flag=flag

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.english_name==rhs.english_name
                and self.position==rhs.position
                and self.parent_index==rhs.parent_index
                and self.layer==rhs.layer
                and self.flag==rhs.flag
                )

    def getConnectionFlag(self):
        return self.flag & 0x0001

    def getIkFlag(self):
        return (self.flag & 0x0020) >> 5

    def getRotationFlag(self):
        return (self.flag & 0x0100) >> 8

    def getTranslationFlag(self):
        return (self.flag & 0x0200) >> 9

    def getFixedAxisFlag(self):
        return (self.flag & 0x0400) >> 10

    def getLocalCoordinateFlag(self):
        return (self.flag &  0x0800) >> 11
    
    def getExternalParentDeformFlag(self):
        return (self.flag &  0x2000) >> 13

 
class Material(object):
    """material

    Attributes: see __init__
    """
    __slots__=[
            'name',
            'english_name',
            'diffuse_color',
            'alpha',
            'specular_color',
            'specular_factor',
            'ambient_color',
            'flag',
            'edge_color',
            'edge_size',
            'texture_index',
            'sphere_texture_index',
            'sphere_mode',
            'toon_sharing_flag',
            'toon_texture_index',
            'comment',
            'vertex_count',
            ]
    def __init__(self,
            name,
            english_name,
            diffuse_color,
            alpha,
            specular_color,
            specular_factor,
            ambient_color,
            flag,
            edge_color,
            edge_size,
            texture_index,
            sphere_texture_index,
            sphere_mode,
            toon_sharing_flag
            ):
        self.name=name
        self.english_name=english_name
        self.diffuse_color=diffuse_color
        self.alpha=alpha
        self.specular_color=specular_color
        self.specular_factor=specular_factor
        self.ambient_color=ambient_color
        self.flag=flag
        self.edge_color=edge_color
        self.edge_size=edge_size
        self.texture_index=texture_index
        self.sphere_texture_index=sphere_texture_index
        self.sphere_mode=sphere_mode
        self.toon_sharing_flag=toon_sharing_flag
        #
        self.toon_texture_index=None
        self.comment=name.__class__() # unicode
        self.vertex_count=0

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.english_name==rhs.english_name
                and self.diffuse_color==rhs.diffuse_color
                and self.alpha==rhs.alpha
                and self.specular_color==rhs.specular_color
                and self.specular_factor==rhs.specular_factor
                and self.ambient_color==rhs.ambient_color
                and self.flag==rhs.flag
                and self.edge_color==rhs.edge_color
                and self.edge_size==rhs.edge_size
                and self.texture_index==rhs.texture_index
                and self.sphere_texture_index==rhs.sphere_texture_index
                and self.sphere_mode==rhs.sphere_mode
                and self.toon_sharing_flag==rhs.toon_sharing_flag
                and self.toon_texture_index==rhs.toon_texture_index
                and self.comment==rhs.comment
                and self.vertex_count==rhs.vertex_count
                )

    def __str__(self):
        return ("<pmx.Material {name}>".format(
            name=self.english_name
            ))


class Deform(object):
    pass


class Bdef1(object):
    """bone deform. use a weight

    Attributes: see __init__
    """
    __slots__=[ 'index0']
    def __init__(self, index0):
        self.index0=index0

    def __eq__(self, rhs):
        return self.index0==rhs.index0


class Bdef2(object):
    """bone deform. use two weights

    Attributes: see __init__
    """
    __slots__=[ 'index0', 'index1', 'weight0']
    def __init__(self, 
            index0,
            index1,
            weight0):
        self.index0=index0
        self.index1=index1
        self.weight0=weight0

    def __eq__(self, rhs):
        return (
                self.index0==rhs.index0
                and self.index1==rhs.index1
                and self.weight0==rhs.weight0
                )


class Vertex(object):
    """pmx vertex

    Attributes: see __init__
    """
    __slots__=[ 'position', 'normal', 'uv', 'deform', 'edge_factor' ]
    def __init__(self, 
            position, 
            normal, 
            uv, 
            deform, 
            edge_factor):
        self.position=position 
        self.normal=normal
        self.uv=uv
        self.deform=deform
        self.edge_factor=edge_factor

    def __eq__(self, rhs):
        return (
                self.position==rhs.position
                and self.normal==rhs.normal
                and self.uv==rhs.uv
                and self.deform==rhs.deform
                and self.edge_factor==rhs.edge_factor
                )


class Morph(object):
    """pmx morph

    Attributes:
        name: 
        english_name: 
        panel:
        morph_type:
        offsets:
    """
    __slots__=[
            'name',
            'english_name',
            'panel',
            'morph_type',
            'offsets',
            ]
    def __init__(self, name, english_name, panel, morph_type):
        self.name=name
        self.english_name=english_name
        self.panel=panel
        self.morph_type=morph_type
        self.offsets=[]

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.english_name==rhs.english_name
                and self.panel==rhs.panel
                and self.morph_type==rhs.morph_type
                and self.offsets==rhs.offsets
                )


class VerexMorphOffset(object):
    """pmx vertex morph offset

    Attributes:
        vertex_index:
        position_offset: Vector3
    """
    __slots__=[
            'vertex_index',
            'position_offset',
            ]
    def __init__(self, vertex_index, position_offset):
        self.vertex_index=vertex_index
        self.position_offset=position_offset

    def __eq__(self, rhs):
        return (
                self.vertex_index==rhs.vertex_index 
                and self.position_offset==rhs.position_offset
                )


class DisplaySlot(object):
    """pmx display slot

    Attributes:
        name: 
        english_name: 
        special_flag:
        refrences: list of (ref_type, ref_index)
    """
    __slots__=[
            'name',
            'english_name',
            'special_flag',
            'refrences',
            ]
    def __init__(self, name, english_name, special_flag):
        self.name=name
        self.english_name=english_name
        self.special_flag=special_flag
        self.refrences=[]

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.english_name==rhs.english_name
                and self.special_flag==rhs.special_flag
                and self.refrences==rhs.refrences
                )


class RigidBodyParam(object):
    """pmx rigidbody param(for bullet)

    Attributes:
        mass:
        linear_damping:
        angular_damping:
        restitution:
        friction:
    """
    __slots__=[
            'mass',
            'linear_damping',
            'angular_damping',
            'restitution',
            'friction',
            ]
    def __init__(self, mass, 
            linear_damping, angular_damping, restitution, friction):
        self.mass=mass
        self.linear_damping=linear_damping
        self.angular_damping=angular_damping
        self.restitution=restitution
        self.friction=friction

    def __eq__(self, rhs):
        return (
                self.mass==rhs.mass
                and self.linear_damping==rhs.linear_damping
                and self.angular_damping==rhs.angular_damping
                and self.restitution==rhs.restitution
                and self.friction==rhs.friction
                )


class RigidBody(object):
    """pmx rigidbody

    Attributes:
        name: 
        english_name: 
        bone_index:
        collision_group:
        no_collision_group:
        shape:
        param:
        mode:
    """
    __slots__=[
            'name',
            'english_name',
            'bone_index',
            'collision_group',
            'no_collision_group',
            'shape_type',
            'shape_size',
            'shape_position',
            'shape_rotation',
            'param',
            'mode',
            ]
    def __init__(self,
            name,
            english_name,
            bone_index,
            collision_group,
            no_collision_group,
            shape_type,
            shape_size,
            shape_position,
            shape_rotation,
            mass,
            linear_damping,
            angular_damping,
            restitution,
            friction,
            mode
            ):
        self.name=name
        self.english_name=english_name
        self.bone_index=bone_index
        self.collision_group=collision_group
        self.no_collision_group=no_collision_group
        self.shape_type=shape_type
        self.shape_size=shape_size
        self.shape_position=shape_position
        self.shape_rotation=shape_rotation
        self.param=RigidBodyParam(mass,
                linear_damping, angular_damping,
                restitution, friction)
        self.mode=mode

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.english_name==rhs.english_name
                and self.bone_index==rhs.bone_index
                and self.collision_group==rhs.collision_group
                and self.no_collision_group==rhs.no_collision_group
                and self.shape_type==rhs.shape_type
                and self.shape_size==rhs.shape_size
                and self.param==rhs.param
                and self.mode==rhs.mode
                )


class Joint(object):
    """pmx joint

    Attributes:
        name: 
        english_name: 
        joint_type:
        rigidbody_index_a:
        rigidbody_index_b:
        position: Vector3
        rotation: Vector3
        translation_limit_min: Vector3
        translation_limit_max: Vector3
        rotation_limit_min: Vector3
        rotation_limit_max: Vector3
        spring_constant_translation: Vector3
        spring_constant_rotation: Vector3
    """
    __slots__=[
            'name',
            'english_name',
            'joint_type',
            'rigidbody_index_a',
            'rigidbody_index_b',
            'position',
            'rotation',
            'translation_limit_min',
            'translation_limit_max',
            'rotation_limit_min',
            'rotation_limit_max',
            'spring_constant_translation',
            'spring_constant_rotation',
            ]
    def __init__(self, name, english_name,
            joint_type,
            rigidbody_index_a,
            rigidbody_index_b,
            position,
            rotation,
            translation_limit_min,
            translation_limit_max,
            rotation_limit_min,
            rotation_limit_max,
            spring_constant_translation,
            spring_constant_rotation
            ):
        self.name=name
        self.english_name=english_name
        self.joint_type=joint_type
        self.rigidbody_index_a=rigidbody_index_a
        self.rigidbody_index_b=rigidbody_index_b
        self.position=position
        self.rotation=rotation
        self.translation_limit_min=translation_limit_min
        self.translation_limit_max=translation_limit_max
        self.rotation_limit_min=rotation_limit_min
        self.rotation_limit_max=rotation_limit_max
        self.spring_constant_translation=spring_constant_translation
        self.spring_constant_rotation=spring_constant_rotation

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.english_name==rhs.english_name
                and self.joint_type==rhs.joint_type
                and self.rigidbody_index_a==rhs.rigidbody_index_a
                and self.rigidbody_index_b==rhs.rigidbody_index_b
                and self.position==rhs.position
                and self.rotation==rhs.rotation
                and self.translation_limit_min==rhs.translation_limit_min
                and self.translation_limit_max==rhs.translation_limit_max
                and self.rotation_limit_min==rhs.rotation_limit_min
                and self.rotation_limit_max==rhs.rotation_limit_max
                and self.spring_constant_translation==rhs.spring_constant_translation
                and self.spring_constant_rotation==rhs.spring_constant_rotation
                )


class Model(object):
    """pmx data representation

    Attributes:
        version: pmx version(expected 2.0)
        name: 
        english_name: 
        comment: 
        english_comment: 
        vertices:
        textures:
        materials:
        bones:
        morph:
        display_slots:
        rigidbodies:
        joints:
    """
    __slots__=[
            'version', # pmx version
            'name', # model name
            'english_name', # model name in english
            'comment', # model comment
            'english_comment', # model comment in english
            'vertices',
            'indices',
            'textures',
            'materials',
            'bones',
            'morphs',
            'display_slots',
            'rigidbodies',
            'joints',
            ]
    def __init__(self, version):
        self.version=version
        self.name=''
        self.english_name=''
        self.comment=''
        self.english_comment=''
        self.vertices=[]
        self.indices=[]
        self.textures=[]
        self.materials=[]
        self.bones=[]
        self.morphs=[]
        self.display_slots=[]
        self.rigidbodies=[]
        self.joints=[]

    def __str__(self):
        return ('<pmx-{version} "{name}" {vertices}vertices>'.format(
            version=self.version,
            name=self.english_name,
            vertices=len(self.vertices)
            ))

    def __eq__(self, rhs):
        return (
                self.version==rhs.version
                and self.name==rhs.name
                and self.english_name==rhs.english_name
                and self.comment==rhs.comment
                and self.english_comment==rhs.english_comment
                and self.vertices==rhs.vertices
                and self.indices==rhs.indices
                and self.textures==rhs.textures
                and self.materials==rhs.materials
                and self.bones==rhs.bones
                and self.morphs==rhs.morphs
                and self.display_slots==rhs.display_slots
                and self.rigidbodies==rhs.rigidbodies
                and self.joints==rhs.joints
                )

