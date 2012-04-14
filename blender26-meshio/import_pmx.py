# coding: utf-8
"""
PMXモデルをインポートする。

1マテリアル、1オブジェクトで作成する。
PMDはPMXに変換してからインポートする。
"""
from . import bl
from .pymeshio import pmx
import bpy
import os


def convert_coord(pos):
    """
    Left handed y-up to Right handed z-up
    """
    return (pos.x, pos.z, pos.y)

def VtoV(v):
    return bl.createVector(v.x, v.y, v.z)

def get_object_name(fmt, index, name):
    """
    object名を作る。最大21バイト
    """
    len_list=[len(name[:i].encode('utf-8')) for i in range(1, len(name)+1, 1)]
    letter_count=0
    prefix=fmt.format(index)
    max_length=21-len(prefix)
    for str_len in len_list:
        if str_len>max_length:
            break
        letter_count+=1
    name=prefix+name[:letter_count]
    #print("%s(%d)" % (name, letter_count))
    return name

def __import_joints(joints, rigidbodies):
    print("create joints")
    container=bl.object.createEmpty('Joints')
    layers=[
        True, False, False, False, False, False, False, False, False, False,
        False, False, False, False, False, False, False, False, False, False,
            ]
    material=bl.material.create('joint')
    material.diffuse_color=(1, 0, 0)
    constraintMeshes=[]
    for i, c in enumerate(joints):
        bpy.ops.mesh.primitive_uv_sphere_add(
                segments=8,
                ring_count=4,
                size=0.1,
                location=(c.position.x, c.position.z, c.position.y),
                layers=layers
                )
        meshObject=bl.object.getActive()
        constraintMeshes.append(meshObject)
        mesh=bl.object.getData(meshObject)
        bl.mesh.addMaterial(mesh, material)
        meshObject.name=get_object_name("j{0:02}:", i, c.name)
        #meshObject.draw_transparent=True
        #meshObject.draw_wire=True
        meshObject.draw_type='SOLID'
        rot=c.rotation
        meshObject.rotation_euler=(-rot.x, -rot.z, -rot.y)

        meshObject[bl.CONSTRAINT_NAME]=c.name
        meshObject[bl.CONSTRAINT_A]=rigidbodies[c.rigidbody_index_a].name
        meshObject[bl.CONSTRAINT_B]=rigidbodies[c.rigidbody_index_b].name
        meshObject[bl.CONSTRAINT_POS_MIN]=VtoV(c.translation_limit_min)
        meshObject[bl.CONSTRAINT_POS_MAX]=VtoV(c.translation_limit_max)
        meshObject[bl.CONSTRAINT_ROT_MIN]=VtoV(c.rotation_limit_min)
        meshObject[bl.CONSTRAINT_ROT_MAX]=VtoV(c.rotation_limit_max)
        meshObject[bl.CONSTRAINT_SPRING_POS]=VtoV(c.spring_constant_translation)
        meshObject[bl.CONSTRAINT_SPRING_ROT]=VtoV(c.spring_constant_rotation)

    for meshObject in reversed(constraintMeshes):
        bl.object.makeParent(container, meshObject)

    return container

def __importRigidBodies(rigidbodies, bones):
    print("create rigid bodies")

    container=bl.object.createEmpty('RigidBodies')
    layers=[
        True, False, False, False, False, False, False, False, False, False,
        False, False, False, False, False, False, False, False, False, False,
            ]
    material=bl.material.create('rigidBody')
    rigidMeshes=[]
    for i, rigid in enumerate(rigidbodies):
        if rigid.bone_index==-1:
            # no reference bone
            bone=bones[0]
        else:
            bone=bones[rigid.bone_index]
        pos=rigid.shape_position
        size=rigid.shape_size

        if rigid.shape_type==0:
            bpy.ops.mesh.primitive_ico_sphere_add(
                    location=(pos.x, pos.z, pos.y),
                    layers=layers
                    )
            bpy.ops.transform.resize(
                    value=(size.x, size.x, size.x))
        elif rigid.shape_type==1:
            bpy.ops.mesh.primitive_cube_add(
                    location=(pos.x, pos.z, pos.y),
                    layers=layers
                    )
            bpy.ops.transform.resize(
                    value=(size.x, size.z, size.y))
        elif rigid.shape_type==2:
            bpy.ops.mesh.primitive_cylinder_add(
                    location=(pos.x, pos.z, pos.y),
                    layers=layers
                    )
            bpy.ops.transform.resize(
                    value=(size.x, size.x, size.y))
        else:
            assert(False)

        meshObject=bl.object.getActive()
        mesh=bl.object.getData(meshObject)
        rigidMeshes.append(meshObject)
        bl.mesh.addMaterial(mesh, material)
        meshObject.name=get_object_name("r{0:02}:", i, rigid.name)
        #meshObject.draw_transparent=True
        #meshObject.draw_wire=True
        meshObject.draw_type='WIRE'
        rot=rigid.shape_rotation
        meshObject.rotation_euler=(-rot.x, -rot.z, -rot.y)

        meshObject[bl.RIGID_NAME]=rigid.name
        meshObject[bl.RIGID_SHAPE_TYPE]=rigid.shape_type
        meshObject[bl.RIGID_PROCESS_TYPE]=rigid.mode
        meshObject[bl.RIGID_BONE_NAME]=bone.name
        meshObject[bl.RIGID_GROUP]=rigid.collision_group
        meshObject[bl.RIGID_INTERSECTION_GROUP]=rigid.no_collision_group
        meshObject[bl.RIGID_WEIGHT]=rigid.param.mass
        meshObject[bl.RIGID_LINEAR_DAMPING]=rigid.param.linear_damping
        meshObject[bl.RIGID_ANGULAR_DAMPING]=rigid.param.angular_damping
        meshObject[bl.RIGID_RESTITUTION]=rigid.param.restitution
        meshObject[bl.RIGID_FRICTION]=rigid.param.friction

    for meshObject in reversed(rigidMeshes):
        bl.object.makeParent(container, meshObject)

    return container

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
    used_bone_name=set()
    for b, bone in zip(bones, bl_bones):
        if b.name!=bone.name:
            if b.name in used_bone_name:
                print("duplicated bone name:[%s][%s]" %(b.name, bone.name))
            else:
                print("invalid name:[%s][%s]" %(b.name, bone.name))
        used_bone_name.add(b.name)
        if b.parent_index!=-1:
            #print("%s -> %s" % (bones[b.parent_index].name, b.name))
            parent_bone=bl_bones[b.parent_index]
            bone.parent=parent_bone
            if b.getConnectionFlag() and b.tail_index!=-1:
                assert(b.tail_index!=0)
                tail_bone=bl_bones[b.tail_index]
                bone.tail=tail_bone.head
                bl.bone.setConnected(tail_bone)
        else:
            #print("no parent %s" % b.name)
            pass
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

        if b.get
    bl.armature.makeEditable(armature_object)
    bl.armature.update(armature)

    # create bone group
    bl.enterObjectMode()
    pose = bl.object.getPose(armature_object)
    bone_groups={}
    for i, ds in enumerate(display_slots):
        print(ds)
        for target, index in ds.references:
            print(target, index)
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


def import_pmx_model(filepath, use_englishmap, model):
    if not model:
        print("fail to load %s" % filepath)
        return False
    print(model)
    print('use_englishmap', use_englishmap)

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
        armature_object.parent=root_object

    # テクスチャを作る
    texture_dir=os.path.dirname(filepath)
    textures_and_images=[bl.texture.create(os.path.join(texture_dir, t))
            for t in model.textures]
    print(textures_and_images)

    index_generator=(i for i in model.indices)
    # 頂点配列。(Left handed y-up) to (Right handed z-up)
    vertices=[convert_coord(pos)
            for pos in (v.position for v in model.vertices)]

    for i, m in enumerate(model.materials):
        name=get_object_name("{0:02}:", i, m.name)
        ####################
        # material
        ####################
        material=__create_a_material(m, name, textures_and_images)

        ####################
        # mesh object
        ####################
        # object名はutf-8で21byteまで
        mesh, mesh_object=bl.mesh.create(name)
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
        assert(len(model.vertices)==len(mesh.vertices))

        # assign material
        bl.mesh.addUV(mesh)
        hasTexture=bl.material.hasTexture(material)
        if hasTexture:
            index_gen=(i for i in indices)
            image=(textures_and_images.get[m.texture_index] 
                    if m.texture_index in textures_and_images
                    else None)
        for i, face in enumerate(bl.mesh.getFaces(mesh)):
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

            # set smooth
            bl.face.setSmooth(face, True)

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

    # import rigid bodies
    rigidbody_object=__importRigidBodies(model.rigidbodies, model.bones)
    if rigidbody_object:
        bl.object.makeParent(root_object, rigidbody_object)

    # import joints
    joint_object=__import_joints(model.joints, model.rigidbodies)
    if joint_object:
        bl.object.makeParent(root_object, joint_object)

    return {'FINISHED'}


def _execute(filepath, use_englishmap, **kwargs):
    """
    importer 本体
    """
    if filepath.lower().endswith(".pmd"):
        from .pymeshio.pmd import reader
        pmd_model=reader.read_from_file(filepath)
        if not pmd_model:
            return

        print("convert pmd to pmx...")
        from .pymeshio import converter
        import_pmx_model(filepath, use_englishmap, 
                converter.pmd_to_pmx(pmd_model))

    elif filepath.lower().endswith(".pmx"):
        from .pymeshio.pmx import reader
        import_pmx_model(filepath, use_englishmap, 
                reader.read_from_file(filepath))

    else:
        print("unknown file type: ", filepath)

