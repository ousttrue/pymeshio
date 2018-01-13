from logging import getLogger
logger = getLogger(__name__)

import pathlib
here = pathlib.Path(__file__).parent
import sys
sys.path.append(str(here.parent))

import unittest


GLTF_MODEL_DIR = here.parent / 'glTF-Sample-Models/2.0'



class GltfTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_triangle(self):
        path = GLTF_MODEL_DIR / 'Triangle/glTF/Triangle.gltf'
        gltf = Gltf(path.parent)
        gltf.load_from_json(path.read_text(encoding='utf-8'))
        self.assertEqual('2.0', gltf.version)

        # meshes
        self.assertEqual(1, len(gltf.meshes))
        mesh = gltf.meshes[0].primitives[0]
        self.assertEqual(0, mesh.indices[0])
        self.assertEqual(1, mesh.indices[1])
        self.assertEqual(2, mesh.indices[2])
        self.assertEqual(0, mesh.positions[0].x)
        self.assertEqual(0, mesh.positions[0].y)
        self.assertEqual(0, mesh.positions[0].z)


if __name__ == '__main__':
    from logging import basicConfig, DEBUG
    basicConfig(
        level=DEBUG,
        datefmt='%H:%M:%S',
        format='%(asctime)s[%(levelname)s][%(name)s.%(funcName)s] %(message)s'
    )
    unittest.main()
