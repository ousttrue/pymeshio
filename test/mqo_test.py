import pymeshio.mqo
import sys

MQO_FILE="K:/model/cube.mqo"

def test_mqo_load():
    io=pymeshio.mqo.IO()
    assert io.read(MQO_FILE)

