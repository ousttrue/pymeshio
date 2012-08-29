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
    material[bl.MATERIALFLAG_BOTHFACE]=m.hasFlag(pmx.MATERIALFLAG_BOTHFACE)
    material[bl.MATERIALFLAG_GROUNDSHADOW]=m.hasFlag(pmx.MATERIALFLAG_GROUNDSHADOW)
    material[bl.MATERIALFLAG_SELFSHADOWMAP]=m.hasFlag(pmx.MATERIALFLAG_SELFSHADOWMAP)
    material[bl.MATERIALFLAG_SELFSHADOW]=m.hasFlag(pmx.MATERIALFLAG_SELFSHADOW)
    material[bl.MATERIALFLAG_EDGE]=m.hasFlag(pmx.MATERIALFLAG_EDGE)
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


def __create_armature(bones):
    """
    :Params:
        bones
            list of pymeshio.pmx.Bone
    """
    armature, armature_object=bl.armature.create()

    # numbering
    for i, b in enumerate(bones): 
        b.index=i

    # create bones
    bl.armature.makeEditable(armature_object)
    def create_bone(b):
        bone=bl.armature.createBone(armature, b.name)
        bone[bl.BONE_ENGLISH_NAME]=b.english_name
        # bone position
        bone.head=bl.createVector(b.position.x, b.position.y, b.position.z)
        if b.getConnectionFlag():
            # dummy tail
            bone.tail=bone.head+bl.createVector(0, 1, 0)
        else:
            # offset tail
            bone.tail=bone.head+bl.createVector(
                    b.tail_position.x, b.tail_position.y, b.tail_position.z)
            if bone.tail==bone.head:
                # 捻りボーン
                bone.tail=bone.head+bl.createVector(0, 0.01, 0)
            pass
        if not b.getVisibleFlag():
            # dummy tail
            bone.tail=bone.head+bl.createVector(0, 0.01, 0)
        return bone
    bl_bones=[create_bone(b) for b in bones]

    # build skeleton
    used_bone_name=set()
    for b, bone in zip(bones, bl_bones):
        if b.name!=bone.name:
            if b.name in used_bone_name:
                print("duplicated bone name:[%s][%s]" %(b.name, bone.name))
            else:
                print("invalid name:[%s][%s]" %(b.name, bone.name))
        used_bone_name.add(b.name)
        if b.parent_index!=-1:
            # set parent
            parent_bone=bl_bones[b.parent_index]
            bone.parent=parent_bone

        if b.getConnectionFlag() and b.tail_index!=-1:
            assert(b.tail_index!=0)
            # set tail position
            tail_bone=bl_bones[b.tail_index]
            bone.tail=tail_bone.head
            # connect with child
            tail_b=bones[b.tail_index]
            if bones[tail_b.parent_index]==b:
                # connect with tail
                bl.bone.setConnected(tail_bone)

    bl.armature.update(armature)

    # pose bone construction
    bl.enterObjectMode()
    pose = bl.object.getPose(armature_object)
    for b in bones:
        p_bone=pose.bones[b.name]
        if b.hasFlag(pmx.BONEFLAG_IS_IK):
            # create ik constraint
            ik=b.ik
            assert(len(ik.link)<16)
            ik_p_bone=pose.bones[bones[ik.target_index].name]
            assert(ik_p_bone)
            bl.constraint.addIk(
                    ik_p_bone, 
                    armature_object, b.name,
                    ik.link, ik.limit_radian, ik.loop)
            armature.bones[b.name][bl.IK_UNITRADIAN]=ik.limit_radian
            for chain in ik.link:
                if chain.limit_angle:
                    ik_p_bone=pose.bones[bones[chain.bone_index].name]
                    # IK limit
                    # x
                    if chain.limit_min.x==0 and chain.limit_max.x==0:
                        ik_p_bone.lock_ik_x=True
                    else:
                        ik_p_bone.use_ik_limit_x=True
                        # left handed to right handed ?
                        ik_p_bone.ik_min_x=-chain.limit_max.x
                        ik_p_bone.ik_max_x=-chain.limit_min.x

                    # y
                    if chain.limit_min.y==0 and chain.limit_max.y==0:
                        ik_p_bone.lock_ik_y=True
                    else:
                        ik_p_bone.use_ik_limit_y=True
                        ik_p_bone.ik_min_y=chain.limit_min.y
                        ik_p_bone.ik_max_y=chain.limit_max.y

                    # z
                    if chain.limit_min.z==0 and chain.limit_max.z==0:
                        ik_p_bone.lock_ik_z=True
                    else:
                        ik_p_bone.use_ik_limit_z=True
                        ik_p_bone.ik_min_z=chain.limit_min.z
                        ik_p_bone.ik_max_z=chain.limit_max.z

        if b.hasFlag(pmx.BONEFLAG_IS_EXTERNAL_ROTATION):
            constraint_p_bone=pose.bones[bones[b.effect_index].name]
            bl.constraint.addCopyRotation(p_bone,
                    armature_object, constraint_p_bone, 
                    b.effect_factor)

        if b.hasFlag(pmx.BONEFLAG_HAS_FIXED_AXIS):
            bl.constraint.addLimitRotation(p_bone)

        if b.parent_index!=-1:
            parent_b=bones[b.parent_index]
            if (
                    parent_b.hasFlag(pmx.BONEFLAG_TAILPOS_IS_BONE)
                    and parent_b.tail_index==b.index
                    ):
                # 移動制限を尻尾位置の接続フラグに流用する
                bl.constraint.addLimitTranslateion(p_bone)
            else:
                parent_parent_b=bones[parent_b.parent_index]
                if (
                        parent_parent_b.hasFlag(pmx.BONEFLAG_TAILPOS_IS_BONE)
                        and parent_parent_b.tail_index==b.index
                        ):
                    # 移動制限を尻尾位置の接続フラグに流用する
                    bl.constraint.addLimitTranslateion(p_bone)

        if not b.hasFlag(pmx.BONEFLAG_CAN_TRANSLATE):
            # translatation lock
            p_bone.lock_location=(True, True, True)


    bl.armature.makeEditable(armature_object)
    bl.armature.update(armature)

    # create bone group
    '''
    bl.enterObjectMode()
    pose = bl.object.getPose(armature_object)
    bone_groups={}
    for i, ds in enumerate(display_slots):
        #print(ds)
        g=bl.object.createBoneGroup(armature_object, ds.name, "THEME%02d" % (i+1))
        for t, index in ds.references:
            if t==0:
                name=bones[index].name
                try:
                    pose.bones[name].bone_group=g
                except KeyError as e:
                    print("pose %s is not found" % name)
                    '''

    bl.enterObjectMode()

    # fix flag
    boneNameMap={}
    for b in bones:
        boneNameMap[b.name]=b
    for b in armature.bones.values():
        if not boneNameMap[b.name].hasFlag(pmx.BONEFLAG_IS_VISIBLE):
            b.hide=True
        if not boneNameMap[b.name].hasFlag(pmx.BONEFLAG_TAILPOS_IS_BONE):
            b[bl.BONE_USE_TAILOFFSET]=True

    return armature_object


def import_pymeshio_model(model, import_mesh=True):
    # メッシュをまとめるエンプティオブジェクト
    root_object=bl.object.createEmpty(__trim_by_utf8_21byte(model.name))
    root_object[bl.MMD_MB_NAME]=model.name
    root_object[bl.MMD_ENGLISH_NAME]=model.english_name
    root_object[bl.MMD_MB_COMMENT]=model.comment
    root_object[bl.MMD_ENGLISH_COMMENT]=model.english_comment

    # armatureを作る
    armature_object=__create_armature(model.bones)
    if armature_object:
        armature_object.parent=root_object

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
            vertices=[v.position.to_tuple() for v in m.vertices]
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
            mesh.update()


            ####################
            # armature
            ####################
            if armature_object:
                # armature modifirer
                bl.modifier.addArmature(mesh_object, armature_object)

            '''
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

