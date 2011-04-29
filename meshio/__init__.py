bl_info = {
    "name": "meshio. (.pmd)(.mqo)",
    "author": "ousttrue",
    "blender": (2, 5, 7),
    "api": 35622,
    "location": "File > Import-Export",
    "description": "Import-Export PMD/MQO meshes",
    "warning": "",
    "url": "http://meshio.sourceforge.jp/",
    "tracker_url": "",
    "support": 'COMMUNITY',
    "category": "Import-Export"
}

# To support reload properly, try to access a package var, if it's there, reload everything
if "bpy" in locals():
    import imp
    if "import_pmd" in locals():
        imp.reload(import_pmd)
    if "export_pmd" in locals():
        imp.reload(export_pmd)


import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty
from io_utils import ImportHelper, ExportHelper
from . import bl25 as bl


'''
PMD IMOPORTER
'''
class ImportPmd(bpy.types.Operator, ImportHelper):
    '''Import from PMD file format (.pmd)'''
    bl_idname = "import_scene.mmd_pmd"
    bl_label = 'Import PMD'

    filename_ext = ".pmd"
    filter_glob = StringProperty(default="*.pmd", options={'HIDDEN'})

    def execute(self, context):
        from . import import_pmd
        bl.initialize('pmd_import', context.scene)
        import_pmd._execute(**self.as_keywords(
            ignore=("filter_glob",)))
        bl.finalize()
        return {'FINISHED'}

def menu_pmd_import(self, context):
    self.layout.operator(ImportPmd.bl_idname,
            text="MikuMikuDance model (.pmd)",
            icon='PLUGIN'
            )


'''
PMD EXPORTER
'''
class ExportPMD(bpy.types.Operator, ExportHelper):
    '''Export to PMD file format (.pmd)'''
    bl_idname = "export_scene.mmd_pmd"
    bl_label = 'Export PMD'

    filename_ext = ".pmd"
    filter_glob = StringProperty(default="*.pmd", options={'HIDDEN'})

    use_selection = BoolProperty(name="Selection Only", description="Export selected objects only", default=False)

    def execute(self, context):
        from . import export_pmd
        bl.initialize('pmd_export', context.scene)
        export_pmd._execute(**self.as_keywords(
            ignore=("check_existing", "filter_glob", "use_selection")))
        bl.finalize()
        return {'FINISHED'}

def menu_pmd_export(self, context):
    default_path=bpy.data.filepath.replace(".blend", ".pmd")
    self.layout.operator(
            ExportPMD.bl_idname,
            text="Miku Miku Dance Model(.pmd)",
            icon='PLUGIN'
            ).filepath=default_path


'''
MQO IMPORTER
'''
class ImportMQO(bpy.types.Operator, ImportHelper):
    '''Import from MQO file format (.mqo)'''
    bl_idname = "import_scene.metasequioa_mqo"
    bl_label = 'Import MQO'

    filename_ext = ".mqo"
    filter_glob = StringProperty(default="*.mqo", options={'HIDDEN'})

    scale = bpy.props.FloatProperty(
            name="Scale",
            description="Scale the MQO by this value",
            min=0.0001, max=1000000.0,
            soft_min=0.001, soft_max=100.0, default=0.1)

    def execute(self, context):
        from . import import_mqo
        bl.initialize('mqo_import', scene)
        import_mqo._execute(**self.as_keywords(
            ignore=("filter_glob",)))
        bl.finalize()
        return {'FINISHED'}

def menu_mqo_import(self, context):
    self.layout.operator(
            ImportMQO.bl_idname,
            text="Metasequoia (.mqo)",
            icon='PLUGIN'
            )


'''
MQO EXPORTER
'''
class ExportMQO(bpy.types.Operator, ExportHelper):
    '''Save a Metasequoia MQO file.'''
    bl_idname = "export_scene.metasequioa_mqo"
    bl_label = 'Export MQO'

    filename_ext = ".mqo"
    filter_glob = StringProperty(default="*.mqo", options={'HIDDEN'})

    use_selection = BoolProperty(name="Selection Only", description="Export selected objects only", default=False)

    scale = bpy.props.FloatProperty(
            name="Scale",
            description="Scale the MQO by this value",
            min=0.0001, max=1000000.0,
            soft_min=0.001, soft_max=100.0, default=10.0)

    apply_modifier = bpy.props.BoolProperty(
            name="ApplyModifier",
            description="Would apply modifiers",
            default=False)

    def execute(self, context):
        from . import export_mqo
        export_pmd._execute(**self.as_keywords(
            ignore=("check_existing", "filter_glob", "use_selection")))
        return {'FINISHED'}

def menu_mqo_export(self, context):
    default_path=bpy.data.filepath.replace(".blend", ".mqo")
    self.layout.operator(
            ExportMQO.bl_idname,
            text="Metasequoia (.mqo)",
            icon='PLUGIN'
            ).filepath=default_path


'''
REGISTER
'''
def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_pmd_import)
    bpy.types.INFO_MT_file_export.append(menu_pmd_export)
    bpy.types.INFO_MT_file_import.append(menu_mqo_import)
    bpy.types.INFO_MT_file_export.append(menu_mqo_export)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_pmd_import)
    bpy.types.INFO_MT_file_export.remove(menu_pmd_export)
    bpy.types.INFO_MT_file_import.remove(menu_mqo_import)
    bpy.types.INFO_MT_file_export.remove(menu_mqo_export)

if __name__ == "__main__":
    register()

