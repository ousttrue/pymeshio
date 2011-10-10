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



class DifferenceException(Exception):
    pass


class Diff(object):
    def _diff(self, rhs, key):
        l=getattr(self, key)
        r=getattr(rhs, key)
        if l!=r:
            print(l)
            print(r)
            raise DifferenceException(key)

    def _diff_array(self, rhs, key):
        la=getattr(self, key)
        ra=getattr(rhs, key)
        if len(la)!=len(ra):
            raise DifferenceException("%s diffrence %d with %d" % (key, len(la), len(ra)))
        for i, (l, r) in enumerate(zip(la, ra)):
            if isinstance(l, Diff):
                try:
                    l.diff(r)
                except DifferenceException as e:
                    print(i)
                    print(l)
                    print(r)
                    raise DifferenceException("{0}: {1}".format(key, e.message))
            else:
                if l!=r:
                    print(i)
                    print(l)
                    print(r)
                    raise DifferenceException("{0}".format(key))


class Ik(Diff):
    """ik info
    """
    __slots__=[
            'target_index',
            'loop',
            'limit_radian',
            'link',
            ]
    def __init__(self, target_index, loop, limit_radian, link=[]):
        self.target_index=target_index
        self.loop=loop
        self.limit_radian=limit_radian
        self.link=link

    def __eq__(self, rhs):
        return (
                self.target_index==rhs.target_index
                and self.loop==rhs.loop
                and self.limit_radian==rhs.limit_radian
                and self.link==rhs.link
                )

    def diff(self, rhs):
        self._diff(rhs, 'target_index')
        self._diff(rhs, 'loop')
        self._diff(rhs, 'limit_radian')
        self._diff_array(rhs, 'link')


class IkLink(Diff):
    """ik link info
    """
    __slots__=[
            'bone_index',
            'limit_angle',
            'limit_min',
            'limit_max',
            ]
    def __init__(self, bone_index, limit_angle, limit_min=common.Vector3(), limit_max=common.Vector3()):
        self.bone_index=bone_index
        self.limit_angle=limit_angle
        self.limit_min=limit_min
        self.limit_max=limit_max

    def __eq__(self, rhs):
        return (
                self.bone_index==rhs.bone_index
                and self.limit_angle==rhs.limit_angle
                and self.limit_min==rhs.limit_min
                and self.limit_max==rhs.limit_max
                )

    def diff(self, rhs):
        self._diff(rhs, 'bone_index')
        self._diff(rhs, 'limit_angle')
        self._diff(rhs, 'limit_min')
        self._diff(rhs, 'limit_max')


class Bone(Diff):
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

            'tail_position',
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
            flag,
            tail_position=common.Vector3(),
            tail_index=-1,
            effect_index=-1,
            effect_factor=0.0,
            fixed_axis=common.Vector3(),
            local_x_vector=common.Vector3(),
            local_z_vector=common.Vector3(),
            external_key=-1,
            ik=None
            ):
        self.name=name
        self.english_name=english_name
        self.position=position
        self.parent_index=parent_index
        self.layer=layer
        self.flag=flag
        self.tail_position=tail_position
        self.tail_index=tail_index
        self.effect_index=effect_index
        self.effect_factor=effect_factor
        self.fixed_axis=fixed_axis
        self.local_x_vector=local_x_vector
        self.local_z_vector=local_z_vector
        self.external_key=external_key
        self.ik=ik

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.english_name==rhs.english_name
                and self.position==rhs.position
                and self.parent_index==rhs.parent_index
                and self.layer==rhs.layer
                and self.flag==rhs.flag
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def diff(self, rhs):
        self._diff(rhs, 'name')
        self._diff(rhs, 'english_name')
        self._diff(rhs, 'position')
        self._diff(rhs, 'parent_index')
        #self._diff(rhs, 'layer')
        self._diff(rhs, 'flag')
        self._diff(rhs, 'tail_position')
        self._diff(rhs, 'tail_index')
        #self._diff(rhs, 'effect_index')
        #self._diff(rhs, 'effect_factor')
        #self._diff(rhs, 'fixed_axis')
        self._diff(rhs, 'local_x_vector')
        self._diff(rhs, 'local_z_vector')
        self._diff(rhs, 'external_key')
        if self.ik and rhs.ik:
            self.ik.diff(rhs.ik)
        else:
            self._diff(rhs, 'ik')

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

 
class Material(Diff):
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
            specular_factor,
            specular_color,
            ambient_color,
            flag,
            edge_color,
            edge_size,
            texture_index,
            sphere_texture_index,
            sphere_mode,
            toon_sharing_flag,
            toon_texture_index=0,
            comment=common.unicode(""),
            vertex_count=0,
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
        self.toon_texture_index=toon_texture_index
        self.comment=comment
        self.vertex_count=vertex_count

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

    def diff(self, rhs):
        #self._diff(rhs, "name")
        self._diff(rhs, "english_name")
        self._diff(rhs, "diffuse_color")
        self._diff(rhs, "alpha")
        self._diff(rhs, "specular_color")
        self._diff(rhs, "specular_factor")
        self._diff(rhs, "ambient_color")
        self._diff(rhs, "flag")
        self._diff(rhs, "edge_color")
        self._diff(rhs, "edge_size")
        self._diff(rhs, "texture_index")
        self._diff(rhs, "sphere_texture_index")
        self._diff(rhs, "sphere_mode")
        self._diff(rhs, "toon_sharing_flag")
        self._diff(rhs, "toon_texture_index")
        self._diff(rhs, "comment")
        self._diff(rhs, "vertex_count")

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def __str__(self):
        return ("<pmx.Material {name}>".format(
            name=self.english_name
            ))


class Bdef1(Diff):
    """bone deform. use a weight

    Attributes: see __init__
    """
    __slots__=[ 'index0']
    def __init__(self, index0):
        self.index0=index0

    def __str__(self):
        return "<Bdef1 {0}>".format(self.index0)

    def __eq__(self, rhs):
        return self.index0==rhs.index0

    def __ne__(self, rhs):
        return not self.__eq__(rhs)


class Bdef2(Diff):
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

    def __str__(self):
        return "<Bdef2 {0}, {1}, {2}>".format(self.index0, self.index1, self.weight0)

    def __eq__(self, rhs):
        return (
                self.index0==rhs.index0
                and self.index1==rhs.index1
                #and self.weight0==rhs.weight0
                and abs(self.weight0-rhs.weight0)<1e-5
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)


class Vertex(Diff):
    """
    ==========
    pmx vertex
    ==========

    :IVariables:
        position
            Vector3
        normal 
            Vector3
        uv 
            Vector2
        deform
            Bdef1, Bdef2 or Bdef4
        edge_factor
            float
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

    def __str__(self):
        return "<Vertex position:{0}, normal:{1}, uv:{2}, deform:{3}, edge:{4}".format(
                self.position, self.normal, self.uv, self.deform, self.edge_factor
                )

    def __eq__(self, rhs):
        return (
                self.position==rhs.position
                and self.normal==rhs.normal
                and self.uv==rhs.uv
                and self.deform==rhs.deform
                and self.edge_factor==rhs.edge_factor
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def diff(self, rhs):
        self._diff(rhs, "position")
        self._diff(rhs, "normal")
        self._diff(rhs, "uv")
        self._diff(rhs, "deform")
        self._diff(rhs, "edge_factor")


class Morph(Diff):
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
    def __init__(self, name, english_name, panel, morph_type, offsets=[]):
        self.name=name
        self.english_name=english_name
        self.panel=panel
        self.morph_type=morph_type
        self.offsets=offsets

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.english_name==rhs.english_name
                and self.panel==rhs.panel
                and self.morph_type==rhs.morph_type
                and self.offsets==rhs.offsets
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def diff(self, rhs):
        self._diff(rhs, 'name')
        self._diff(rhs, 'english_name')
        #self._diff(rhs, 'panel')
        self._diff(rhs, 'morph_type')
        self._diff_array(rhs, 'offsets')


class VerexMorphOffset(Diff):
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

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def diff(self, rhs):
        self._diff(rhs, 'vertex_index')
        self._diff(rhs, 'position_offset')


class DisplaySlot(Diff):
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
    def __init__(self, name, english_name, special_flag, refrences=[]):
        self.name=name
        self.english_name=english_name
        self.special_flag=special_flag
        self.refrences=refrences

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.english_name==rhs.english_name
                and self.special_flag==rhs.special_flag
                and self.refrences==rhs.refrences
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def diff(self, rhs):
        self._diff(rhs, 'name')
        self._diff(rhs, 'english_name')
        self._diff(rhs, 'special_flag')
        #self._diff_array(rhs, 'refrences')


class RigidBodyParam(Diff):
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

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def diff(self, rhs):
        self._diff(rhs, 'mass')
        self._diff(rhs, 'linear_damping')
        self._diff(rhs, 'angular_damping')
        self._diff_array(rhs, 'restitution')
        self._diff_array(rhs, 'friction')


class RigidBody(Diff):
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

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def diff(self, rhs):
        self._diff(rhs, 'name')
        self._diff(rhs, 'english_name')
        self._diff(rhs, 'bone_index')
        self._diff(rhs, 'collision_group')
        self._diff(rhs, 'no_collision_group')
        self._diff(rhs, 'shape_type')
        self._diff(rhs, 'shape_size')
        #self._diff(rhs, 'shape_position')
        self._diff(rhs, 'shape_rotation')
        self._diff(rhs, 'param')
        self._diff(rhs, 'mode')


class Joint(Diff):
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

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def diff(self, rhs):
        self._diff(rhs, 'name')
        self._diff(rhs, 'joint_type')
        self._diff(rhs, 'rigidbody_index_a')
        self._diff(rhs, 'rigidbody_index_b')
        self._diff(rhs, 'position')
        self._diff(rhs, 'rotation')
        self._diff(rhs, 'translation_limit_min')
        self._diff(rhs, 'translation_limit_max')
        self._diff(rhs, 'rotation_limit_min')
        self._diff(rhs, 'rotation_limit_max')
        self._diff(rhs, 'spring_constant_translation')
        self._diff(rhs, 'spring_constant_rotation')


class Model(Diff):
    """
    ==========
    pmx model
    ==========

    :IVariables:
        version
            pmx version(expected 2.0)
        name 
            model name
        english_name 
            model name
        comment 
            comment
        english_comment 
            comment
        vertices
            vertex list
        textures
            texture list
        materials
            material list
        bones
            bone list
        morph
            morph list
        display_slots
            display list for bone/morph grouping
        rigidbodies
            bullet physics rigidbody list
        joints
            bullet physics joint list
    """
    __slots__=[
            'path',
            'version',
            'name',
            'english_name',
            'comment',
            'english_comment',
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
    def __init__(self, version=2.0):
        self.path=''
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

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def diff(self, rhs):
        self._diff(rhs, "version")
        self._diff(rhs, "name")
        self._diff(rhs, "english_name")
        self._diff(rhs, "comment")
        self._diff(rhs, "english_comment")
        self._diff_array(rhs, "vertices")
        self._diff_array(rhs, "indices")
        self._diff_array(rhs, "textures")
        self._diff_array(rhs, "materials")
        self._diff_array(rhs, "bones")
        self._diff_array(rhs, "morphs")
        self._diff_array(rhs, "display_slots")
        self._diff_array(rhs, "rigidbodies")
        self._diff_array(rhs, "joints")

