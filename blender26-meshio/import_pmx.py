# coding: utf-8
"""
PMXモデルをインポートする。

1マテリアル、1オブジェクトで作成する。
"""
import os
from . import bl


def __create_a_material(m, name, textures_and_images):
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

def _execute(filepath):
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
    root=bl.object.createEmpty(model_name)
    root[bl.MMD_MB_NAME]=model.name
    root[bl.MMD_MB_COMMENT]=model.comment
    root[bl.MMD_COMMENT]=model.english_comment

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
    vertices=[(pos.x, pos.z, pos.y) 
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
        bl.object.makeParent(root, mesh_object)
        indices=[next(index_generator) 
                    for _ in range(m.vertex_count)]
        bl.mesh.addGeometry(mesh, vertices, 
                [(indices[i], indices[i+1], indices[i+2]) 
                    for i in range(0, len(indices), 3)])

    return {'FINISHED'}

