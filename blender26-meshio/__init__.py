# coding: utf-8

bl_info={
        'category': 'Import-Export',
        'name': 'extended MikuMikuDance model format(.pmx)',
        'author': 'ousttrue',
        'blender': (2, 6, 0),
        'location': 'File > Import-Export',
        'description': 'Import from the extended MikuMikuDance Model Format(.pmx)',
        'warning': '', # used for warning icon and text in addons panel
        'wiki_url': 'http://sourceforge.jp/projects/meshio/wiki/FrontPage',
        }

if "bpy" in locals():
    import imp
    if "import_pmx" in locals():
        imp.reaload(import_pmx)


import bpy
import bpy_extras


class ImportPMX(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    '''Import from the extended MikuMikuDance Model Format(.pmx)'''
    bl_idname='import_scene.mmd_pmx'
    bl_label='Import PMX'
    bl_options={'UNDO'}
    filename_ext='.pmx'
    filter_glob=bpy.props.StringProperty(
            default="*.pmx", options={'HIDDEN'})


    def execute(self, context):
        from . import import_pmx
        keywords=self.as_keywords()
        return import_pmx.load(self, context, **keywords)


def menu_func_import(self, context):
    self.layout.operator(ImportPMX.bl_idname, 
            text="MikuMikuDance model (.pmx)",
            icon='PLUGIN'
            )

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__=="__main__":
    register()

