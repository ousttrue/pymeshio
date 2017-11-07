import os

if 'PYMESHIO_TEST_RESOURCES' in os.environ:
    PYMESHIO_TEST_RESOURCES = os.path.abspath(os.environ['PYMESHIO_TEST_RESOURCES'])
else:
    PYMESHIO_TEST_RESOURCES = os.path.abspath("./resources")
