# coding: utf-8
"""
PMXモデルをインポートする。

1マテリアル、1オブジェクトで作成する。
"""
import os
from . import bl


def convert_coord(pos):
    """
    Left handed y-up to Right handed z-up
    """
    return (pos.x, pos.z, pos.y)

def __create_a_material(m, name, textures_and_images):
    """
    materialを作成する

    :Params:
        m
            pymeshio.pmx.Material
        name
            material name
        textures_and_images
            list of (texture, image)
    """
    material = bl.material.create(name)
    # diffuse
    material.diffuse_shader='FRESNEL'
    material.diffuse_color=[m.diffuse_color.r, m.diffuse_color.g, m.diffuse_color.b]
    material.alpha=m.alpha
    # specular
    material.specular_shader='TOON'
    material.specular_color=[m.specular_color.r, m.specular_color.g, m.specular_color.b]
    material.specular_toon_size=int(m.specular_factor)
    # ambient
    material.mirror_color=[m.ambient_color.r, m.ambient_color.g, m.ambient_color.b]
    # todo
    # flag
    # edge_color
    # edge_size
    # other
    material.preview_render_type='FLAT'
    material.use_transparency=True
    # texture
    texture_index=bl.material.addTexture(material, textures_and_images[m.texture_index][0])
    return material

def __create_armature(bones):
    """
    armatureを作成する

    :Params:
        bones
            list of pymeshio.pmx.Bone
    """
    armature, armature_object=bl.armature.create()

    bl.armature.makeEditable(armature_object)
    # create bones
    def create_bone(b):
        bone=bl.armature.createBone(armature, b.name)
        # bone position
        bone.head=bl.createVector(*convert_coord(b.position))
        if not b.getConnectionFlag():
            bone.tail=bl.createVector(*convert_coord(b.position))
        elif not b.getVisibleFlag():
            bone.tail=bone.head+bl.createVector(0, 1, 0)

        return bone
    bl_bones=[create_bone(b) for b in bones]

    # build skeleton
    for b, bone in zip(bones, bl_bones):
        if b.parent_index!=-1:
            print("%s -> %s" % (bones[b.parent_index].name, b.name))
            parent_bone=bl_bones[b.parent_index]
            bone.parent=parent_bone
            if b.getConnectionFlag() and b.tail_index!=-1:
                assert(b.tail_index!=0)
                tail_bone=bl_bones[b.tail_index]
                bone.tail=tail_bone.head
                bl.bone.setConnected(tail_bone)
        else:
            print("no parent %s" % b.name)

    # fix
    bl.armature.update(armature)
    bl.enterObjectMode()

    return armature_object

def _execute(filepath):
    """
    importerr 本体
    """
    bl.progress_set('load %s' % filepath, 0.0)
    print(filepath)

    from .pymeshio.pmx import reader
    model=reader.read_from_file(filepath)
    if not model:
        print("fail to load %s" % filepath)
        return
    print(model)
    bl.progress_set('loaded', 0.1)

    # メッシュをまとめるエンプティオブジェクト
    model_name=model.english_name
    if len(model_name)==0:
        model_name=os.path.basename(filepath)
    root_object=bl.object.createEmpty(model_name)
    root_object[bl.MMD_MB_NAME]=model.name
    root_object[bl.MMD_MB_COMMENT]=model.comment
    root_object[bl.MMD_COMMENT]=model.english_comment

    # armatureを作る
    armature_object=__create_armature(model.bones)
    if armature_object:
        bl.object.makeParent(root_object, armature_object)

    # テクスチャを作る
    texture_dir=os.path.dirname(filepath)
    textures_and_images=[bl.texture.create(os.path.join(texture_dir, t))
            for t in model.textures]
    print(textures_and_images)

    def get_name(name, fmt, *args):
        if len(name.encode("utf-8"))<16:
            return name
        else:
            return fmt.format(*args)
    index_generator=(i for i in model.indices)
    # 頂点配列。(Left handed y-up) to (Right handed z-up)
    vertices=[convert_coord(pos)
            for pos in (v.position for v in model.vertices)]
    for i, m in enumerate(model.materials):
        # マテリアル毎にメッシュを作成する
        print(m.name)
        #material=__create_a_material(m, get_name(m.name, "material:{0:02}", i), textures_and_images)
        material=__create_a_material(m, m.name, textures_and_images)
        mesh, mesh_object=bl.mesh.create("object:{0:02}".format(i))
        bl.mesh.addMaterial(mesh, material)
        # activate object
        bl.object.deselectAll()
        bl.object.activate(mesh_object)
        bl.object.makeParent(root_object, mesh_object)
        # vertices & faces
        indices=[next(index_generator)
                    for _ in range(m.vertex_count)]
        bl.mesh.addGeometry(mesh, vertices,
                [(indices[i], indices[i+1], indices[i+2])
                    for i in range(0, len(indices), 3)])
        if armature_object:
            # armature modifirer
            bl.modifier.addArmature(mesh_object, armature_object)

        # shape


    return {'FINISHED'}

