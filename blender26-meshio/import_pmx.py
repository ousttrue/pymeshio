# coding: utf-8
"""
PMXモデルをインポートする。

1マテリアル、1オブジェクトで作成する。
"""
import os
from . import bl
from .pymeshio import pmx
from .pymeshio.pmx import reader


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
    if m.texture_index!=-1:
        bl.material.addTexture(material, textures_and_images[m.texture_index][0])
    return material

def __create_armature(bones, display_slots):
    """
    armatureを作成する

    :Params:
        bones
            list of pymeshio.pmx.Bone
    """
    armature, armature_object=bl.armature.create()

    # create bones
    bl.armature.makeEditable(armature_object)
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
        assert(b.name==bone.name)
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
    bl.armature.update(armature)

    # create ik constraint
    bl.enterObjectMode()
    pose = bl.object.getPose(armature_object)
    for b, bone in zip(bones, bl_bones):
        if b.getIkFlag():
            ik=b.ik
            assert(len(ik.link)<16)
            p_bone=pose.bones[bones[ik.target_index].name]
            assert(p_bone)
            constraint=bl.armature.createIkConstraint(
                    armature_object, p_bone, bone.name,
                    ik.link, ik.limit_radian, ik.loop)
    bl.armature.makeEditable(armature_object)
    bl.armature.update(armature)

    # create bone group
    bl.enterObjectMode()
    pose = bl.object.getPose(armature_object)
    for i, ds in enumerate(display_slots):
        print(ds)
        g=bl.object.createBoneGroup(armature_object, ds.name, "THEME%02d" % (i+1))
        for t, index in ds.references:
            if t==0:
                name=bones[index].name
                try:
                    pose.bones[name].bone_group=g
                except KeyError as e:
                    print("pose %s is not found" % name)

    bl.enterObjectMode()
    return armature_object

def _execute(filepath):
    """
    importerr 本体
    """
    bl.progress_set('load %s' % filepath, 0.0)
    print(filepath)

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
    armature_object=__create_armature(model.bones, model.display_slots)
    if armature_object:
        bl.object.makeParent(root_object, armature_object)

    # テクスチャを作る
    texture_dir=os.path.dirname(filepath)
    textures_and_images=[bl.texture.create(os.path.join(texture_dir, t))
            for t in model.textures]
    print(textures_and_images)

    index_generator=(i for i in model.indices)
    # 頂点配列。(Left handed y-up) to (Right handed z-up)
    vertices=[convert_coord(pos)
            for pos in (v.position for v in model.vertices)]

    # マテリアル毎にメッシュを作成する
    def get_object_name(index, name):
        """
        object名を作る。最大21バイト
        """
        len_list=[len(name[:i].encode('utf-8')) for i in range(1, len(name)+1, 1)]
        letter_count=0
        for str_len in len_list:
            if str_len<18: # 21-3
                letter_count+=1
            else:
                break
        name="{0:02}:{1}".format(index, name[:letter_count])
        print("%s(%d)" % (name, letter_count))
        return name
    for i, m in enumerate(model.materials):
        ####################
        # material
        ####################
        material=__create_a_material(m, m.name, textures_and_images)

        ####################
        # mesh object
        ####################
        # object名はutf-8で21byteまで
        mesh, mesh_object=bl.mesh.create(get_object_name(i, m.name))
        bl.mesh.addMaterial(mesh, material)
        # activate object
        bl.object.deselectAll()
        bl.object.activate(mesh_object)
        bl.object.makeParent(root_object, mesh_object)

        ####################
        # vertices & faces
        ####################
        indices=[next(index_generator)
                    for _ in range(m.vertex_count)]
        used_indices=set(indices)
        bl.mesh.addGeometry(mesh, vertices,
                [(indices[i], indices[i+1], indices[i+2])
                    for i in range(0, len(indices), 3)])
        assert(len(model.vertices), len(mesh.vertices))

        # assign material
        bl.mesh.addUV(mesh)
        hasTexture=bl.material.hasTexture(material)
        if hasTexture:
            index_gen=(i for i in indices)
            image=(textures_and_images.get[m.texture_index] 
                    if m.texture_index in textures_and_images
                    else None)
        for i, face in enumerate(mesh.faces):
            bl.face.setMaterial(face, 0)
            if hasTexture:
                uv0=model.vertices[next(index_gen)].uv
                uv1=model.vertices[next(index_gen)].uv
                uv2=model.vertices[next(index_gen)].uv
                bl.mesh.setFaceUV(mesh, i, face, [# fix uv
                    (uv0.x, 1.0-uv0.y),
                    (uv1.x, 1.0-uv1.y),
                    (uv2.x, 1.0-uv2.y)
                    ],
                    image)

        ####################
        # armature
        ####################
        if armature_object:
            # armature modifirer
            bl.modifier.addArmature(mesh_object, armature_object)
            # set vertex attributes(normal, bone weights)
            bl.mesh.useVertexUV(mesh)
            for i, (v,  mvert) in enumerate(zip(model.vertices, mesh.vertices)):
                bl.vertex.setNormal(mvert, convert_coord(v.normal))
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

        ####################
        # shape keys
        ####################
        # set shape_key pin
        bl.object.pinShape(mesh_object, True)
        # create base key
        baseShapeBlock=bl.object.addShapeKey(mesh_object, bl.BASE_SHAPE_NAME)
        mesh.update()
        for m in model.morphs:
            new_shape_key=bl.object.addShapeKey(mesh_object, m.name)
            for o in m.offsets:
                if isinstance(o, pmx.VertexMorphOffset):
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

    return {'FINISHED'}

