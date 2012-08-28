# coding: utf-8

try:
    import bpy
    from .. import util
except Exception as e:
    pass


def import_file(filepath, **args):

    pymeshio_model=util.GenericModel.read_from_file(filepath)
    if not pymeshio_model:
        print('fail to load: '+filepath)
        return

    print(pymeshio_model)


def export_pmd(filepath, **args):
    print('export_pmd', args)

def export_pmx(filepath, **args):
    print('export_pmx', args)

def export_mqo(filepath, **args):
    print('export_mqo', args)

