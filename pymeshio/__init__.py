
def unicode(src):
    import sys
    if sys.version_info[0]<3:
        return src.decode('utf-8')
    else:
        return src

