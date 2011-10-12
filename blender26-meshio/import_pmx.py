# coding: utf-8

def load(operator, context, filepath, **kw):
    print(filepath)
    print(kw)

    from .pymeshio.pmx import reader
    model=reader.read_from_file(filepath)
    if not model:
        print("fail to load %s" % filepath)
        return
    print(model)

    return {'FINISHED'}

