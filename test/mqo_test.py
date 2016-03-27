import pymeshio.mqo
import pymeshio.mqo.reader
import sys
import os


MQO_FILE="resources/cube.mqo"


def test_mqo_read():
    assert os.path.exists(MQO_FILE), "not exists"
    model=pymeshio.mqo.reader.read_from_file(MQO_FILE)
    assert model, "fail"
    assert pymeshio.mqo.Model==model.__class__, "class"
    assert 1==len(model.materials), "materials"
    assert 1==len(model.objects), "objects"

