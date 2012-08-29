# coding: utf-8

import os
import bpy
import functools
from .. import util
from . import bl
from .. import pmx


def __trim_by_utf8_21byte(src):
    """
    UTF-8で21バイト長になるように調節する
    """
    len_list=[len(src[:i].encode('utf-8')) for i in range(1, len(src)+1, 1)]
    max_length=21
    letter_count=0
    for str_len in len_list:
        if str_len>max_length:
            break
        letter_count+=1
    return src[:letter_count]


def __get_object_name(fmt, index, name):
    """
    object名を作る。最大21バイト
    """
    return __trim_by_utf8_21byte(fmt.format(index)+name)


def __create_a_material(m, i, textures_and_images):
    """
    materialを作成する

    :Params:
        m
            Material
        i
            material index
        textures_and_images
            list of (texture, image)
    """
    name=__get_object_name("{0:02}:", i, m.name)
    material = bl.material.create(name)
    # diffuse
    material.diffuse_shader='FRESNEL'
    material.diffuse_color=[
            m.diffuse_color.r, m.diffuse_color.g, m.diffuse_color.b]
    material.alpha=m.alpha
    # specular
    material.specular_shader='TOON'
    material.specular_color=[
            m.specular_color.r, m.specular_color.g, m.specular_color.b]
    material.specular_toon_size=m.specular_factor * 0.1
    # ambient
    material.mirror_color=[
            m.ambient_color.r, m.ambient_color.g, m.ambient_color.b]
    # flag
    # ToDo:
    #material[bl.MATERIALFLAG_BOTHFACE]=m.hasFlag(pmx.MATERIALFLAG_BOTHFACE)
    #material[bl.MATERIALFLAG_GROUNDSHADOW]=m.hasFlag(pmx.MATERIALFLAG_GROUNDSHADOW)
    #material[bl.MATERIALFLAG_SELFSHADOWMAP]=m.hasFlag(pmx.MATERIALFLAG_SELFSHADOWMAP)
    #material[bl.MATERIALFLAG_SELFSHADOW]=m.hasFlag(pmx.MATERIALFLAG_SELFSHADOW)
    #material[bl.MATERIALFLAG_EDGE]=m.hasFlag(pmx.MATERIALFLAG_EDGE)
    # edge_color
    # edge_size
    # other
    material.preview_render_type='FLAT'
    material.use_transparency=True
    # texture
    if m.texture_index!=-1:
        texture=textures_and_images[m.texture_index][0]
        bl.material.addTexture(material, texture)
    # toon texture
    if m.toon_sharing_flag==1:
        material[bl.MATERIAL_SHAREDTOON]=m.toon_texture_index
    else:
        if m.toon_texture_index!=-1:
            toon_texture=textures_and_images[m.toon_texture_index][0]
            toon_texture[bl.TEXTURE_TYPE]='TOON'
            bl.material.addTexture(material, toon_texture)
    # sphere texture
    if m.sphere_mode==pmx.MATERIALSPHERE_NONE:
        material[bl.MATERIAL_SPHERE_MODE]=pmx.MATERIALSPHERE_NONE
    elif m.sphere_mode==pmx.MATERIALSPHERE_SPH:
        # SPH
        if m.sphere_texture_index==-1:
            material[bl.MATERIAL_SPHERE_MODE]=pmx.MATERIALSPHERE_NONE
        else:
            sph_texture=textures_and_images[m.sphere_texture_index][0]
            sph_texture[bl.TEXTURE_TYPE]='SPH'
            bl.material.addTexture(material, sph_texture)
            material[bl.MATERIAL_SPHERE_MODE]=m.sphere_mode
    elif m.sphere_mode==pmx.MATERIALSPHERE_SPA:
        # SPA
        if m.sphere_texture_index==-1:
            material[bl.MATERIAL_SPHERE_MODE]=pmx.MATERIALSPHERE_NONE
        else:
            spa_texture=textures_and_images[m.sphere_texture_index][0]
            spa_texture[bl.TEXTURE_TYPE]='SPA'
            bl.material.addTexture(material, spa_texture)
            material[bl.MATERIAL_SPHERE_MODE]=m.sphere_mode
    else:
        print("unknown sphere mode:", m.sphere_mode)
    return material


def import_pymeshio_model(model, import_mesh=True):
    # メッシュをまとめるエンプティオブジェクト
    root_object=bl.object.createEmpty(__trim_by_utf8_21byte(model.name))
    root_object[bl.MMD_MB_NAME]=model.name
    root_object[bl.MMD_ENGLISH_NAME]=model.english_name
    root_object[bl.MMD_MB_COMMENT]=model.comment
    root_object[bl.MMD_ENGLISH_COMMENT]=model.english_comment

    '''
    # armatureを作る
    armature_object=__create_armature(model.bones, model.display_slots)
    if armature_object:
        armature_object.parent=root_object
    '''

    if import_mesh:
        # テクスチャを作る
        texture_dir=os.path.dirname(model.filepath)
        print(model.textures)
        textures_and_images=[bl.texture.create(os.path.join(texture_dir, t))
                for t in model.textures]
        print(textures_and_images)

        # マテリアルを作る
        materials=[__create_a_material(m, i, textures_and_images) 
                for i, m in enumerate(model.materials)]

        # 画像
        images=[(textures_and_images.get[m.texture_index] 
            if (m.texture_index in textures_and_images)
            else None) 
            for m in model.materials]

        for i, m in enumerate(model.meshes):
            ####################
            # mesh object
            ####################
            # object名はutf-8で21byteまで
            mesh, mesh_object=bl.mesh.create('submesh')
            # activate object
            bl.object.deselectAll()
            bl.object.activate(mesh_object)
            bl.object.makeParent(root_object, mesh_object)

            ####################
            # material
            ####################
            for material in materials:
                bl.mesh.addMaterial(mesh, material)

            ####################
            # vertices & faces
            ####################
            # 頂点配列
            vertices=[(v.pos.x, v.pos.y, v.pos.z) for v in m.vertices]
            faces=[(f.indices[0], f.indices[1], f.indices[2]) for f in m.faces]
            #used_indices=set(faces)

            bl.mesh.addGeometry(mesh, vertices, faces)
            assert(len(m.vertices)==len(mesh.vertices))

            bl.mesh.addUV(mesh)
            for i, (f, face) in enumerate(zip(m.faces, mesh.tessfaces)):
                bl.face.setMaterial(face, f.material_index)
                uv0=m.vertices[f.indices[0]].uv
                uv1=m.vertices[f.indices[1]].uv
                uv2=m.vertices[f.indices[2]].uv
                bl.mesh.setFaceUV(mesh, i, face, [# fix uv
                    (uv2.x, 1.0-uv2.y),
                    (uv1.x, 1.0-uv1.y),
                    (uv0.x, 1.0-uv0.y)
                    ],
                    images[f.material_index])
                # set smooth
                bl.face.setSmooth(face, True)

            # set vertex attributes(normal, bone weights)
            bl.mesh.useVertexUV(mesh)
            for i, (mvert, v) in enumerate(zip(mesh.vertices, m.vertices)):
                bl.vertex.setNormal(mvert, v.normal.to_tuple())
                '''
                if isinstance(v.deform, pmx.Bdef1):
                    bl.object.assignVertexGroup(mesh_object,
                            model.bones[v.deform.index0].name, i, 1.0)
                elif isinstance(v.deform, pmx.Bdef2):
                    bl.object.assignVertexGroup(mesh_object,
                            model.bones[v.deform.index0].name, i, v.deform.weight0)
                    bl.object.assignVertexGroup(mesh_object,
                            model.bones[v.deform.index1].name, i, 1.0-v.deform.weight0)
                else:
                    raise Exception("unknown deform: %s" % v.deform)
                '''
            mesh.update()


            '''
            ####################
            # armature
            ####################
            if armature_object:
                # armature modifirer
                bl.modifier.addArmature(mesh_object, armature_object)

            ####################
            # shape keys
            ####################
            if len(model.morphs)>0:
                # set shape_key pin
                bl.object.pinShape(mesh_object, True)
                # create base key
                bl.object.addVertexGroup(mesh_object, bl.MMD_SHAPE_GROUP_NAME)
                # assign all vertext to group
                for i, v in enumerate(mesh.vertices):
                    bl.object.assignVertexGroup(mesh_object,
                            bl.MMD_SHAPE_GROUP_NAME, i, 0);
                # create base key
                baseShapeBlock=bl.object.addShapeKey(mesh_object, bl.BASE_SHAPE_NAME)
                mesh.update()

                # each morph
                for m in model.morphs:
                    new_shape_key=bl.object.addShapeKey(mesh_object, m.name)
                    for o in m.offsets:
                        if isinstance(o, pmx.VertexMorphOffset):
                            # vertex morph
                            bl.shapekey.assign(new_shape_key, 
                                    o.vertex_index, 
                                    mesh.vertices[o.vertex_index].co+
                                    bl.createVector(*convert_coord(o.position_offset)))
                        else:
                            raise Exception("unknown morph type: %s" % o)

                # select base shape
                bl.object.setActivateShapeKey(mesh_object, 0)

            #############################
            # clean up not used vertices
            # in the material.
            #############################
            bl.mesh.vertsDelete(mesh, [i for i in range(len(mesh.vertices))
                if i not in used_indices])

            # flip
            #bl.mesh.flipNormals(mesh_object)
            '''
    bl.enterObjectMode()
    bl.object.activate(root_object)


def import_file(scene, filepath, **args):
    bl.initialize('import_file', scene)
    pymeshio_model=util.GenericModel.read_from_file(filepath)
    if not pymeshio_model:
        print('fail to load: '+filepath)
        return

    import_pymeshio_model(pymeshio_model)

def export_pmd(filepath, **args):
    print('export_pmd', args)

def export_pmx(filepath, **args):
    print('export_pmx', args)

def export_mqo(filepath, **args):
    print('export_mqo', args)

