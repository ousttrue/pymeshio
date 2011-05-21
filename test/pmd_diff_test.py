import pymeshio.pmd
import meshio
import sys
from nose.tools import *

PMD_FILE="K:/MMD/model/official/miku.pmd"

def test_pmd_diff():
    io_py=pymeshio.pmd.IO()
    assert io_py.read(PMD_FILE)
    io_c=meshio.pmd.IO()
    assert io_c.read(PMD_FILE)

    # header
    assert_equal(io_py.version, io_c.version)
    assert_equal(io_py.name, io_c.name)
    assert_equal(io_py.english_name, io_c.english_name)
    assert_equal(io_py.comment, io_c.comment)
    assert_equal(io_py.english_comment, io_c.english_comment)

    # vertices
    assert_equal(len(io_py.vertices), len(io_c.vertices))
    for l, r in zip(io_py.vertices, io_c.vertices):
        assert_equal(l.pos.x, r.pos.x)
        assert_equal(l.pos.y, r.pos.y)
        assert_equal(l.pos.z, r.pos.z)
        assert_equal(l.normal.x, r.normal.x)
        assert_equal(l.normal.y, r.normal.y)
        assert_equal(l.normal.z, r.normal.z)
        assert_equal(l.uv.x, r.uv.x)
        assert_equal(l.uv.y, r.uv.y)
        assert_equal(l.bone0, r.bone0)
        assert_equal(l.bone1, r.bone1)
        assert_equal(l.weight0, r.weight0)
        assert_equal(l.edge_flag, r.edge_flag)

    # indices
    assert_equal(len(io_py.indices), len(io_c.indices))
    for l, r in zip(io_py.indices, io_c.indices):
        assert_equal(l, r)

    # materials
    assert_equal(len(io_py.materials), len(io_c.materials))
    for l, r in zip(io_py.materials, io_c.materials):
        assert_equal(l.diffuse.r, r.diffuse.r)
        assert_equal(l.diffuse.g, r.diffuse.g)
        assert_equal(l.diffuse.b, r.diffuse.b)
        assert_equal(l.diffuse.a, r.diffuse.a)
        assert_equal(l.shinness, r.shinness)
        assert_equal(l.specular.r, r.specular.r)
        assert_equal(l.specular.g, r.specular.g)
        assert_equal(l.specular.b, r.specular.b)
        assert_equal(l.ambient.r, r.ambient.r)
        assert_equal(l.ambient.g, r.ambient.g)
        assert_equal(l.ambient.b, r.ambient.b)
        assert_equal(l.vertex_count, r.vertex_count)
        assert_equal(l.texture, r.texture)
        assert_equal(l.toon_index, r.toon_index)
        assert_equal(l.flag, r.flag)

    # bones
    assert_equal(len(io_py.bones), len(io_c.bones))
    for l, r in zip(io_py.bones, io_c.bones):
        assert_equal(l.name, r.name)
        assert_equal(l.type, r.type)
        assert_equal(l.parent_index, r.parent_index)
        assert_equal(l.tail_index, r.tail_index)
        assert_equal(l.tail.x, r.tail.x)
        assert_equal(l.tail.y, r.tail.y)
        assert_equal(l.tail.z, r.tail.z)
        assert_equal(l.ik_index, r.ik_index)
        assert_equal(l.pos.x, r.pos.x)
        assert_equal(l.pos.y, r.pos.y)
        assert_equal(l.pos.z, r.pos.z)
        assert_equal(l.english_name, r.english_name)

    # ik_list
    assert_equal(len(io_py.ik_list), len(io_c.ik_list))
    for l, r in zip(io_py.ik_list, io_c.ik_list):
        assert_equal(l.index, r.index)
        assert_equal(l.target, r.target)
        assert_equal(l.iterations, r.iterations)
        assert_equal(l.weight, r.weight)
        for l_child, r_child in zip(l.children, r.children):
            assert_equal(l_child, r_child)

    # morph_list
    assert_equal(len(io_py.morph_list), len(io_c.morph_list))
    for l, r in zip(io_py.morph_list, io_c.morph_list):
        assert_equal(l.name, r.name)
        assert_equal(l.type, r.type)
        for l_index, r_index in zip(l.indices, r.indices):
            assert_equal(l_index, r_index)
        for l_pos, r_pos in zip(l.pos_list, r.pos_list):
            assert_equal(l_pos.x, l_pos.x)
            assert_equal(l_pos.y, l_pos.y)
            assert_equal(l_pos.z, l_pos.z)
        assert_equal(l.english_name, l.english_name)
        assert_equal(l.vertex_count, l.vertex_count)


    # face_list
    assert_equal(len(io_py.face_list), len(io_c.face_list))
    for l, r in zip(io_py.face_list, io_c.face_list):
        assert_equal(l, r)

    # bone_group_list
    assert_equal(len(io_py.bone_group_list), len(io_c.bone_group_list))
    for l, r in zip(io_py.bone_group_list, io_c.bone_group_list):
        assert_equal(l.name, r.name)
        assert_equal(l.english_name, r.english_name)

    # bone_display_list
    assert_equal(len(io_py.bone_display_list), len(io_c.bone_display_list))
    for l, r in zip(io_py.bone_display_list, io_c.bone_display_list):
        assert_equal(l[0], r[0])
        assert_equal(l[1], r[1])

    # toon_textures
    for l, r in ((io_py.toon_textures[i], io_c.toon_textures[i]) for i in range(10)):
        assert_equal(l, r.str())

    # rigidbodies
    assert_equal(len(io_py.rigidbodies), len(io_c.rigidbodies))
    for l, r in zip(io_py.rigidbodies, io_c.rigidbodies):
        assert_equal(l.name, r.name)
        assert_equal(l.boneIndex, r.boneIndex)
        assert_equal(l.group, r.group)
        assert_equal(l.target, r.target)
        assert_equal(l.shapeType, r.shapeType)
        assert_equal(l.w, r.w)
        assert_equal(l.h, r.h)
        assert_equal(l.d, r.d)
        assert_equal(l.position.x, r.position.x)
        assert_equal(l.position.x, r.position.x)
        assert_equal(l.position.x, r.position.x)
        assert_equal(l.rotation.x, r.rotation.x)
        assert_equal(l.rotation.x, r.rotation.x)
        assert_equal(l.rotation.x, r.rotation.x)
        assert_equal(l.weight, r.weight)
        assert_equal(l.linearDamping, r.linearDamping)
        assert_equal(l.angularDamping, r.angularDamping)
        assert_equal(l.restitution, r.restitution)
        assert_equal(l.friction, r.friction)
        assert_equal(l.processType, r.processType)

    # constraints
    assert_equal(len(io_py.constraints), len(io_c.constraints))
    for l, r in zip(io_py.constraints, io_c.constraints):
        assert_equal(l.name, r.name)
        assert_equal(l.rigidA, r.rigidA)
        assert_equal(l.rigidB, r.rigidB)
        assert_equal(l.pos.x, r.pos.x)
        assert_equal(l.pos.y, r.pos.y)
        assert_equal(l.pos.z, r.pos.z)
        assert_equal(l.rot.x, r.rot.x)
        assert_equal(l.rot.y, r.rot.y)
        assert_equal(l.rot.z, r.rot.z)
        assert_equal(l.constraintPosMin.x, r.constraintPosMin.x)
        assert_equal(l.constraintPosMin.y, r.constraintPosMin.y)
        assert_equal(l.constraintPosMin.z, r.constraintPosMin.z)
        assert_equal(l.constraintPosMax.x, r.constraintPosMax.x)
        assert_equal(l.constraintPosMax.y, r.constraintPosMax.y)
        assert_equal(l.constraintPosMax.z, r.constraintPosMax.z)
        assert_equal(l.constraintRotMin.x, r.constraintRotMin.x)
        assert_equal(l.constraintRotMin.y, r.constraintRotMin.y)
        assert_equal(l.constraintRotMin.z, r.constraintRotMin.z)
        assert_equal(l.constraintRotMax.x, r.constraintRotMax.x)
        assert_equal(l.constraintRotMax.y, r.constraintRotMax.y)
        assert_equal(l.constraintRotMax.z, r.constraintRotMax.z)
        assert_equal(l.springPos.x, r.springPos.x)
        assert_equal(l.springPos.y, r.springPos.y)
        assert_equal(l.springPos.z, r.springPos.z)
        assert_equal(l.springRot.x, r.springRot.x)
        assert_equal(l.springRot.y, r.springRot.y)
        assert_equal(l.springRot.z, r.springRot.z)

