# coding: utf-8

from . import bl


def _execute(filepath):
    print(filepath)
    active=bl.object.getActive()
    if not active:
        print("abort. no active object.")
        return
    exporter=PmdExporter()
    exporter.setup()
    print(exporter)
    exporter.write(filepath)
    bl.object.activate(active)
    return {'FINISHED'}

