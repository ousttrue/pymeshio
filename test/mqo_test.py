from logging import getLogger
logger = getLogger(__name__)

import os

import pymeshio.mqo
import pymeshio.mqo.reader


MQO_FILE = "resources/cube.mqo"


def test_mqo_read():
    if not os.path.exists(MQO_FILE):
        logger.debug("%s not exists", MQO_FILE)
        return
    model = pymeshio.mqo.reader.read_from_file(MQO_FILE)
    assert model, "fail"
    assert pymeshio.mqo.Model == model.__class__, "class"
    assert 1 == len(model.materials), "materials"
    assert 1 == len(model.objects), "objects"
