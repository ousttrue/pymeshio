import pymeshio.x
import pymeshio.x.reader
import sys


FILE="resources/cube.x"


def test_x_read():
    model=pymeshio.x.reader.read_from_file(FILE)
    assert pymeshio.x.Model==model.__class__
    assert 8==len(model.vertices)
    assert 6==len(model.materials)

