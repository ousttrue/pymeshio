import pymeshio.mqo
import pymeshio.mqo.reader
import sys


MQO_FILE="resources/cube.mqo"

def test_old_mqo_load():
    io=pymeshio.mqo.IO()
    assert io.read(MQO_FILE)

def test_mqo_read():
    model=pymeshio.mqo.reader.read_from_file(MQO_FILE)
    print(model.materials)
    assert pymeshio.mqo.Model==model.__class__
    assert 6==len(model.materials)
    assert 1==len(model.objects)

