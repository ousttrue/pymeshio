# coding: utf-8

import io
from . import bl
from . import exporter
from .pymeshio import pmx
from .pymeshio import common
from .pymeshio.pmx import writer


def near(x, y, EPSILON=1e-5):
    d=x-y
    return d>=-EPSILON and d<=EPSILON


def create_pmx(ex):
    """
    PMX 出力
    """
    model=pmx.Model()

    o=ex.root.o
    model.name=o.get(bl.MMD_MB_NAME, 'Blenderエクスポート')
    model.english_name=o.get(bl.MMD_ENGLISH_NAME, 'blender export model')
    model.comment=o.get(bl.MMD_MB_COMMENT, 'Blnderエクスポート\n')
    model.english_comment=o.get(bl.MMD_ENGLISH_COMMENT, 'blender export commen\n')

    def get_deform(b0, b1, weight):
        if b0==-1:
            return pmx.Bdef1(b1, weight)
        elif b1==-1:
            return pmx.Bdef1(b0, weight)
        else:
            return pmx.Bdef2(b0, b1, weight)

    model.vertices=[pmx.Vertex(
        # convert right-handed z-up to left-handed y-up
        common.Vector3(pos[0], pos[2], pos[1]), 
        # convert right-handed z-up to left-handed y-up
        common.Vector3(attribute.nx, attribute.nz, attribute.ny),
        # reverse vertical
        common.Vector2(attribute.u, 1.0-attribute.v),
        get_deform(ex.skeleton.indexByName(b0), ex.skeleton.indexByName(b1), weight),
        # edge flag, 0: enable edge, 1: not edge
        1.0 
        )
        for pos, attribute, b0, b1, weight in ex.oneSkinMesh.vertexArray.zip()]

    boneMap=dict([(b.name, i) for i, b in enumerate(ex.skeleton.bones)])

    def getFixedAxis(b):
        if b.isFixedAxis():
            return common.Vector3(
                    b.tail[0],
                    b.tail[2],
                    b.tail[1]
                    ).normalize()
        else:
            return common.Vector3(0, 0, 0)
    
    def create_bone(b):

        bone=pmx.Bone(
            name=b.name,
            english_name=b.english_name,
            # convert right-handed z-up to left-handed y-up
            position=common.Vector3(
                b.pos[0] if not near(b.pos[0], 0) else 0,
                b.pos[2] if not near(b.pos[2], 0) else 0,
                b.pos[1] if not near(b.pos[1], 0) else 0
                ),
            parent_index=b.parent_index,
            layer=0,
            flag=0,
            tail_position=None,
            tail_index=b.tail_index,
            effect_index=-1,
            effect_factor=0.0,
            fixed_axis=getFixedAxis(b),
            local_x_vector=None,
            local_z_vector=None,
            external_key=-1,
            ik=None
                )

        if b.constraint==exporter.bonebuilder.CONSTRAINT_COPY_ROTATION:
            bone.layer=2
            bone.effect_index=boneMap[b.constraintTarget]
            bone.effect_factor=b.constraintInfluence
            bone.setFlag(pmx.BONEFLAG_IS_EXTERNAL_ROTATION, True)

        if b.constraint==exporter.bonebuilder.CONSTRAINT_LIMIT_ROTATION:
            bone.setFlag(pmx.BONEFLAG_HAS_FIXED_AXIS, True)

        bone.setFlag(pmx.BONEFLAG_TAILPOS_IS_BONE, b.hasTail)
        bone.setFlag(pmx.BONEFLAG_CAN_ROTATE, True)
        bone.setFlag(pmx.BONEFLAG_CAN_TRANSLATE, b.canTranslate)
        bone.setFlag(pmx.BONEFLAG_IS_VISIBLE, b.isVisible)
        bone.setFlag(pmx.BONEFLAG_CAN_MANIPULATE, b.canManipulate())

        if b.ikSolver:
            bone.setFlag(pmx.BONEFLAG_IS_IK, True)
            bone.ik_target_index=b.ikSolver.effector_index
            bone.ik=pmx.Ik(
                    b.ikSolver.effector_index,
                    b.ikSolver.iterations,
                    b.ikSolver.weight,
                    [pmx.IkLink(c.index, c.limitAngle, 
                        common.Vector3(*c.limitMin),
                        common.Vector3(*c.limitMax))
                        for c in b.ikSolver.chain
                        ])

        return bone

    model.bones=[create_bone(b) for b in ex.skeleton.bones]

    # textures
    textures=set()
    def get_texture_name(texture):
        pos=texture.replace("\\", "/").rfind("/")
        if pos==-1:
            return texture
        else:
            return texture[pos+1:]
    for m in ex.oneSkinMesh.vertexArray.indexArrays.keys():
        for path in bl.material.eachEnalbeTexturePath(bl.material.get(m)):
            textures.add(get_texture_name(path))
    model.textures=list(textures)

    # texture pathからtexture indexを逆引き
    texturePathMap={}
    for i, texture_path in enumerate(model.textures):
        texturePathMap[texture_path]=i

    def get_flag(m):
        """
        return material flag
        """
        return (
                m.get(bl.MATERIALFLAG_BOTHFACE, 0)
                +(m.get(bl.MATERIALFLAG_GROUNDSHADOW, 0) << 1)
                +(m.get(bl.MATERIALFLAG_SELFSHADOWMAP, 0) << 2)
                +(m.get(bl.MATERIALFLAG_SELFSHADOW, 0) << 3)
                +(m.get(bl.MATERIALFLAG_EDGE, 0) << 4)
                )

    def get_toon_shareing_flag(m):
        """
        return
        shared: 1
        not shared: 0
        """
        for t in bl.material.eachEnalbeTexturePath(m):
            if re.match("""toon\d\d.bmp"""):
                return 1
        return 0

    def get_texture_params(m, texturePathMap):
        texture_index=-1
        toon_texture_index=-1
        toon_sharing_flag=0
        sphere_texture_index=-1
        sphere_mode=pmx.MATERIALSPHERE_NONE

        for t in bl.material.eachEnalbeTexture(m):
            texture_type=t.get(bl.TEXTURE_TYPE, 'NORMAL')
            texture_path=get_texture_name(bl.texture.getPath(t))
            if texture_type=='NORMAL': 
                texture_index=texturePathMap[texture_path]
            elif texture_type=='TOON':
                toon_texture_index=texturePathMap[texture_path]
                toon_sharing_flag=0
            elif texture_type=='SPH':
                sphere_texture_index=texturePathMap[texture_path]
                sphere_mode=pmx.MATERIALSPHERE_SPH
            elif texture_type=='SPA':
                sphere_texture_index=texturePathMap[texture_path]
                sphere_mode=pmx.MATERIALSPHERE_SPA
        
        if bl.MATERIAL_SHAREDTOON in m:
            toon_texture_index=m[bl.MATERIAL_SHAREDTOON]
            toon_sharing_flag=1

        return (texture_index,
                toon_texture_index, toon_sharing_flag,
                sphere_texture_index, sphere_mode)

    # 面とマテリアル
    vertexCount=ex.oneSkinMesh.getVertexCount()
    for material_name, indices in ex.oneSkinMesh.vertexArray.each():
        #print('material:', material_name)
        try:
            m=bl.material.get(material_name)
        except KeyError as e:
            m=DefaultMatrial()
        (
                texture_index, 
                toon_texture_index, toon_sharing_flag, 
                sphere_texture_index, sphere_mode,
                )=get_texture_params(m, texturePathMap)
        # マテリアル
        model.materials.append(pmx.Material(
                name=m.name,
                english_name='',
                diffuse_color=common.RGB(
                    m.diffuse_color[0], 
                    m.diffuse_color[1], 
                    m.diffuse_color[2]),
                alpha=m.alpha,
                specular_factor=(0 
                    if m.specular_toon_size<1e-5 
                    else m.specular_toon_size * 10),
                specular_color=common.RGB(
                    m.specular_color[0], 
                    m.specular_color[1], 
                    m.specular_color[2]),
                ambient_color=common.RGB(
                    m.mirror_color[0], 
                    m.mirror_color[1], 
                    m.mirror_color[2]),
                flag=get_flag(m),
                edge_color=common.RGBA(0, 0, 0, 1),
                edge_size=1.0,
                texture_index=texture_index,
                sphere_texture_index=sphere_texture_index,
                sphere_mode=sphere_mode,
                toon_sharing_flag=toon_sharing_flag,
                toon_texture_index=toon_texture_index,
                comment='',
                vertex_count=len(indices)
                ))
        # 面
        for i in indices:
            assert(i<vertexCount)
        for i in range(0, len(indices), 3):
            # reverse triangle
            model.indices.append(indices[i+2])
            model.indices.append(indices[i+1])
            model.indices.append(indices[i])

    # 表情
    for i, m in enumerate(ex.oneSkinMesh.morphList):
        morph=pmx.Morph(
                name=m.name,
                english_name='',
                panel=0,
                morph_type=1,
                )
        morph.offsets=[pmx.VertexMorphOffset(
            index, 
            common.Vector3(offset[0], offset[2], offset[1])
            )
            for index, offset in m.offsets]
        model.morphs.append(morph)


    # ボーングループ
    model.display_slots=[pmx.DisplaySlot(
        name=name,
        english_name='',
        special_flag=0,
        )
        for name, members in ex.skeleton.bone_groups]

    # rigid body
    boneNameMap={}
    for i, b in enumerate(ex.skeleton.bones):
        boneNameMap[b.name]=i
    rigidNameMap={}
    for i, obj in enumerate(ex.oneSkinMesh.rigidbodies):
        name=obj[bl.RIGID_NAME] if bl.RIGID_NAME in obj else obj.name
        #print(name)
        rigidNameMap[name]=i
        boneIndex=boneNameMap[obj[bl.RIGID_BONE_NAME]]
        if boneIndex==0:
            boneIndex=-1
            bone=ex.skeleton.bones[0]
        else:
            bone=ex.skeleton.bones[boneIndex]
        if obj[bl.RIGID_SHAPE_TYPE]==0:
            shape_type=0
            shape_size=common.Vector3(obj.scale[0], 0, 0)
        elif obj[bl.RIGID_SHAPE_TYPE]==1:
            shape_type=1
            shape_size=common.Vector3(obj.scale[0], obj.scale[1], obj.scale[2])
        elif obj[bl.RIGID_SHAPE_TYPE]==2:
            shape_type=2
            shape_size=common.Vector3(obj.scale[0], obj.scale[2], 0)
        rigidBody=pmx.RigidBody(
                name=name, 
                english_name='',
                collision_group=obj[bl.RIGID_GROUP],
                no_collision_group=obj[bl.RIGID_INTERSECTION_GROUP],
                bone_index=boneIndex,
                shape_position=common.Vector3(
                    obj.location.x-bone.pos[0],
                    obj.location.z-bone.pos[2],
                    obj.location.y-bone.pos[1]),
                shape_rotation=common.Vector3(
                    -obj.rotation_euler[0],
                    -obj.rotation_euler[2],
                    -obj.rotation_euler[1]),
                shape_type=shape_type,
                shape_size=shape_size,
                mass=obj[bl.RIGID_WEIGHT],
                linear_damping=obj[bl.RIGID_LINEAR_DAMPING],
                angular_damping=obj[bl.RIGID_ANGULAR_DAMPING],
                restitution=obj[bl.RIGID_RESTITUTION],
                friction=obj[bl.RIGID_FRICTION],
                mode=obj[bl.RIGID_PROCESS_TYPE]
                )
        model.rigidbodies.append(rigidBody)

    # joint
    model.joints=[pmx.Joint(
        name=obj[bl.CONSTRAINT_NAME],
        english_name='',
        joint_type=0,
        rigidbody_index_a=rigidNameMap[obj[bl.CONSTRAINT_A]],
        rigidbody_index_b=rigidNameMap[obj[bl.CONSTRAINT_B]],
        position=common.Vector3(
            obj.location[0], 
            obj.location[2], 
            obj.location[1]),
        rotation=common.Vector3(
            -obj.rotation_euler[0], 
            -obj.rotation_euler[2], 
            -obj.rotation_euler[1]),
        translation_limit_min=common.Vector3(
            obj[bl.CONSTRAINT_POS_MIN][0],
            obj[bl.CONSTRAINT_POS_MIN][1],
            obj[bl.CONSTRAINT_POS_MIN][2]
            ),
        translation_limit_max=common.Vector3(
            obj[bl.CONSTRAINT_POS_MAX][0],
            obj[bl.CONSTRAINT_POS_MAX][1],
            obj[bl.CONSTRAINT_POS_MAX][2]
            ),
        rotation_limit_min=common.Vector3(
            obj[bl.CONSTRAINT_ROT_MIN][0],
            obj[bl.CONSTRAINT_ROT_MIN][1],
            obj[bl.CONSTRAINT_ROT_MIN][2]),
        rotation_limit_max=common.Vector3(
            obj[bl.CONSTRAINT_ROT_MAX][0],
            obj[bl.CONSTRAINT_ROT_MAX][1],
            obj[bl.CONSTRAINT_ROT_MAX][2]),
        spring_constant_translation=common.Vector3(
            obj[bl.CONSTRAINT_SPRING_POS][0],
            obj[bl.CONSTRAINT_SPRING_POS][1],
            obj[bl.CONSTRAINT_SPRING_POS][2]),
        spring_constant_rotation=common.Vector3(
            obj[bl.CONSTRAINT_SPRING_ROT][0],
            obj[bl.CONSTRAINT_SPRING_ROT][1],
            obj[bl.CONSTRAINT_SPRING_ROT][2])
        )
        for obj in ex.oneSkinMesh.constraints]

    return model


def _execute(filepath):
    active=bl.object.getActive()
    if not active:
        print("abort. no active object.")
        return

    ex=exporter.Exporter()
    ex.setup()

    model=create_pmx(ex)
    bl.object.activate(active)
    with io.open(filepath, 'wb') as f:
        writer.write(f, model)
    return {'FINISHED'}

