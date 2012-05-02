# coding: utf-8

bl_info={
        'category': 'Import-Export',
        'name': 'meshio. (.pmd)(.pmx)(.mqo)',
        'author': 'ousttrue',
        'blender': (2, 6, 0),
        'location': 'File > Import-Export',
        'description': 'Import-Export PMD/PMX/MQO meshes',
        #'warning': 'pmx importer/exporter is under development', 
        'wiki_url': 'http://meshio.sourceforge.jp/',
        'support': 'COMMUNITY',
        }


# To support reload properly, try to access a package var, if it's there, reload everything
if 'bpy' in locals():
    import imp
    def reload_module(name):
        if name in locals():
            imp.reaload(locals()[name])
    reload_module('import_pmx')
    reload_module('export_pmx')
    reload_module('import_pmd')
    reload_module('export_pmd')
    reload_module('import_mqo')
    reload_module('export_mqo')
   

import bpy
import bpy_extras.io_utils
from . import bl


class ImportPmd(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    '''Import from PMD file format (.pmd)'''
    bl_idname = 'import_scene.mmd_pmd'
    bl_label = 'Import PMD'
    bl_options={'UNDO'}
    filename_ext = '.pmd'
    filter_glob = bpy.props.StringProperty(
            default='*.pmd', options={'HIDDEN'})

    def execute(self, context):
        from . import import_pmd
        bl.initialize('pmd_import', context.scene)
        import_pmd._execute(**self.as_keywords(
            ignore=('filter_glob',)))
        bl.finalize()
        return {'FINISHED'}

    @classmethod
    def menu_func(klass, self, context):
        self.layout.operator(klass.bl_idname,
                text='MikuMikuDance model (.pmd)',
                icon='PLUGIN'
                )


class ImportPmx(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    '''Import from PMX Format(.pmx)(.pmd)'''
    bl_idname='import_scene.mmd_pmx_pmd'
    bl_label='Import PMX/PMD'
    bl_options={'UNDO'}
    filename_ext='.pmx;.pmd'
    filter_glob=bpy.props.StringProperty(
            default='*.pmx;*.pmd', options={'HIDDEN'})

    #use_englishmap=bpy.props.BoolProperty(
    #        name='use english map', 
    #        description='Convert name to english(not implemented)',
    #        default=False)

    import_mesh=bpy.props.BoolProperty(
            name='import mesh', 
            description='import polygon mesh',
            default=True)

    import_physics=bpy.props.BoolProperty(
            name='import physics objects', 
            description='import rigid body and constraints',
            default=True)

    def execute(self, context):
        from . import import_pmx
        bl.initialize('pmx_import', context.scene)
        import_pmx._execute(**self.as_keywords(ignore=('filter_glob',)))
        bl.finalize()
        return  {'FINISHED'}

    @classmethod
    def menu_func(klass, self, context):
        self.layout.operator(klass.bl_idname, 
                text='MikuMikuDance model (.pmx)(.pmd)',
                icon='PLUGIN'
                )


class ImportMqo(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    '''Import from MQO file format (.mqo)'''
    bl_idname = 'import_scene.metasequioa_mqo'
    bl_label = 'Import MQO'
    bl_options={'UNDO'}
    filename_ext = '.mqo'
    filter_glob = bpy.props.StringProperty(
            default='*.mqo', options={'HIDDEN'})

    scale = bpy.props.FloatProperty(
            name='Scale',
            description='Scale the MQO by this value',
            min=0.0001, max=1000000.0,
            soft_min=0.001, soft_max=100.0, default=0.1)

    def execute(self, context):
        from . import import_mqo
        bl.initialize('mqo_import', context.scene)
        import_mqo._execute(**self.as_keywords(
            ignore=('filter_glob',)))
        bl.finalize()
        return {'FINISHED'}

    @classmethod
    def menu_func(klass, self, context):
        self.layout.operator(klass.bl_idname,
                text="Metasequoia (.mqo)",
                icon='PLUGIN'
                )


class ExportPmd(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    '''Export to PMD file format (.pmd)'''
    bl_idname = 'export_scene.mmd_pmd'
    bl_label = 'Export PMD'

    filename_ext = '.pmd'
    filter_glob = bpy.props.StringProperty(
            default='*.pmd', options={'HIDDEN'})

    use_selection = bpy.props.BoolProperty(
            name='Selection Only', 
            description='Export selected objects only', 
            default=False)

    def execute(self, context):
        from . import export_pmd
        bl.initialize('pmd_export', context.scene)
        export_pmd._execute(**self.as_keywords(
            ignore=('check_existing', 'filter_glob', 'use_selection')))
        bl.finalize()
        return {'FINISHED'}

    @classmethod
    def menu_func(klass, self, context):
        default_path=bpy.data.filepath.replace('.blend', '.pmd')
        self.layout.operator(klass.bl_idname,
                text='Miku Miku Dance Model(.pmd)',
                icon='PLUGIN'
                ).filepath=default_path


class ExportPmx(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    '''Export to PMX file format (.pmx)'''
    bl_idname = 'export_scene.mmd_pmx'
    bl_label = 'Export PMX'

    filename_ext = '.pmx'
    filter_glob = bpy.props.StringProperty(
            default='*.pmx', options={'HIDDEN'})

    use_selection = bpy.props.BoolProperty(
            name='Selection Only', 
            description='Export selected objects only', 
            default=False)

    def execute(self, context):
        from . import export_pmx
        bl.initialize('pmx_export', context.scene)
        export_pmx._execute(**self.as_keywords(
            ignore=('check_existing', 'filter_glob', 'use_selection')))
        bl.finalize()
        return {'FINISHED'}

    @classmethod
    def menu_func(klass, self, context):
        default_path=bpy.data.filepath.replace('.blend', '.pmx')
        self.layout.operator(klass.bl_idname,
                text='Miku Miku Dance Model(.pmx)',
                icon='PLUGIN'
                ).filepath=default_path


class ExportMqo(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    '''Save a Metasequoia MQO file.'''
    bl_idname = 'export_scene.metasequioa_mqo'
    bl_label = 'Export MQO'

    filename_ext = '.mqo'
    filter_glob = bpy.props.StringProperty(
            default='*.mqo', options={'HIDDEN'})

    use_selection = bpy.props.BoolProperty(
            name='Selection Only', 
            description='Export selected objects only', 
            default=False)

    scale = bpy.props.FloatProperty(
            name='Scale',
            description='Scale the MQO by this value',
            min=0.0001, max=1000000.0,
            soft_min=0.001, soft_max=100.0, default=10.0)

    apply_modifier = bpy.props.BoolProperty(
            name='ApplyModifier',
            description='Would apply modifiers',
            default=False)

    def execute(self, context):
        from . import export_mqo
        bl.initialize('mqo_export', context.scene)
        export_mqo._execute(**self.as_keywords(
            ignore=('check_existing', 'filter_glob', 'use_selection')))
        bl.finalize()
        return {'FINISHED'}

    @classmethod
    def menu_func(klass, self, context):
        default_path=bpy.data.filepath.replace('.blend', '.mqo')
        self.layout.operator(klass.bl_idname,
                text='Metasequoia (.mqo)',
                icon='PLUGIN'
                ).filepath=default_path


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(ImportPmd.menu_func)
    bpy.types.INFO_MT_file_import.append(ImportPmx.menu_func)
    bpy.types.INFO_MT_file_import.append(ImportMqo.menu_func)
    bpy.types.INFO_MT_file_export.append(ExportPmd.menu_func)
    bpy.types.INFO_MT_file_export.append(ExportPmx.menu_func)
    bpy.types.INFO_MT_file_export.append(ExportMqo.menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(ImportPmd.menu_func)
    bpy.types.INFO_MT_file_import.remove(ImportPmx.menu_func)
    bpy.types.INFO_MT_file_import.remove(ImportMqo.menu_func)
    bpy.types.INFO_MT_file_export.remove(ExportPmd.menu_func)
    bpy.types.INFO_MT_file_export.remove(ExportPmx.menu_func)
    bpy.types.INFO_MT_file_export.remove(ExportMqo.menu_func)


if __name__=='__main__':
    register()

