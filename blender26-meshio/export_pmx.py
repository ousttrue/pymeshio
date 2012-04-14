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
    model.english_name=o.name
    model.name=o[bl.MMD_MB_NAME] if bl.MMD_MB_NAME in o else 'Blenderエクスポート'
    model.comment=o[bl.MMD_MB_COMMENT] if bl.MMD_MB_COMMENT in o else 'Blnderエクスポート\n'
    model.english_comment=o[bl.MMD_COMMENT] if bl.MMD_COMMENT in o else 'blender export\n'

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

    '''
    # IK
    for ik in self.skeleton.ik_list:
        solver=pmd.IK()
        solver.index=self.skeleton.getIndex(ik.target)
        solver.target=self.skeleton.getIndex(ik.effector)
        solver.length=ik.length
        b=self.skeleton.bones[ik.effector.parent_index]
        for i in range(solver.length):
            solver.children.append(self.skeleton.getIndex(b))
            b=self.skeleton.bones[b.parent_index]
        solver.iterations=ik.iterations
        solver.weight=ik.weight
        model.ik_list.append(solver)
    '''
    def create_bone(b):
        return pmx.Bone(
            name=b.name,
            english_name=b.name,
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
            fixed_axis=None,
            local_x_vector=None,
            local_z_vector=None,
            external_key=-1,
            ik=None
                )
    model.bones=[create_bone(b)
            for b in ex.skeleton.bones]

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

    # 面とマテリアル
    vertexCount=ex.oneSkinMesh.getVertexCount()
    for material_name, indices in ex.oneSkinMesh.vertexArray.each():
        #print('material:', material_name)
        try:
            m=bl.material.get(material_name)
        except KeyError as e:
            m=DefaultMatrial()
        # マテリアル
        model.materials.append(pmx.Material(
                name=m.name,
                english_name='',
                diffuse_color=common.RGB(m.diffuse_color[0], m.diffuse_color[1], m.diffuse_color[2]),
                alpha=m.alpha,
                specular_factor=0 if m.specular_toon_size<1e-5 else m.specular_hardness*10,
                specular_color=common.RGB(m.specular_color[0], m.specular_color[1], m.specular_color[2]),
                ambient_color=common.RGB(m.mirror_color[0], m.mirror_color[1], m.mirror_color[2]),
                flag=1 if m.subsurface_scattering.use else 0,
                edge_color=common.RGBA(0, 0, 0, 1),
                edge_size=1.0,
                texture_index=0,
                sphere_texture_index=0,
                sphere_mode=0,
                toon_sharing_flag=0,
                toon_texture_index=0,
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
        print(name)
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

