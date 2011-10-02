import pymeshio.mqo
import pymeshio.mqo.reader
import sys


MQO_FILE="resources/cube.mqo"


def test_mqo_read():
    model=pymeshio.mqo.reader.read_from_file(MQO_FILE)
    assert pymeshio.mqo.Model==model.__class__
    assert 6==len(model.materials)
    assert 1==len(model.objects)

