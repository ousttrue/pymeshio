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

    # indices
    assert_equal(len(io_py.indices), len(io_c.indices))

    # materials
    assert_equal(len(io_py.materials), len(io_c.materials))

    # bones
    assert_equal(len(io_py.bones), len(io_c.bones))

    # ik_list
    assert_equal(len(io_py.ik_list), len(io_c.ik_list))

    # morph_list
    assert_equal(len(io_py.morph_list), len(io_c.morph_list))

    # face_list
    assert_equal(len(io_py.face_list), len(io_c.face_list))

    # bone_group_list
    assert_equal(len(io_py.bone_group_list), len(io_c.bone_group_list))

    # bone_display_list
    assert_equal(len(io_py.bone_display_list), len(io_c.bone_display_list))

    # toon_textures

    # rigidbodies
    assert_equal(len(io_py.rigidbodies), len(io_c.rigidbodies))

    # constraints
    assert_equal(len(io_py.constraints), len(io_c.constraints))

