from .. import common
from .. import pmd
from .. import konbu


@konbu.parser_builder
def pmd_header():
    sig=yield konbu.ascii_of(b'Pmd')
    return sig


@konbu.parser_builder
def pmd_parser():
    model=pmd.Model()
    header = yield pmd_header
    return model

def read_from_bytes(rawbytes: bytes):
    result=pmd_parser(konbu.ParseContext(rawbytes))
    print(result)
    return result.value

def read_from_file(path: str):
    model=read_from_bytes(common.readall(path))
    model.path=path
    return model

