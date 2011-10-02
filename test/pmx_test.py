# coding: utf-8
import unittest
import pymeshio.pmd
import pymeshio.pmx.reader


PMX_FILE=pymeshio.unicode('resources/初音ミクVer2.pmx')


class TestPmx(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_read(self):
        model=pymeshio.pmx.reader.read_from_file(PMX_FILE)
        self.assertEqual(pymeshio.pmx.Model,  model.__class__)
        self.assertEqual(pymeshio.unicode('初音ミク'),  model.name)
        self.assertEqual(pymeshio.unicode('Miku Hatsune'),  model.english_name)
        self.assertEqual(pymeshio.unicode(
                "PolyMo用モデルデータ：初音ミク ver.2.3\r\n"+
                "(物理演算対応モデル)\r\n"+
                "\r\n"+
                "モデリング	：あにまさ氏\r\n"+
                "データ変換	：あにまさ氏\r\n"+
                "Copyright	：CRYPTON FUTURE MEDIA, INC"),
                model.comment)
        self.assertEqual(pymeshio.unicode(
                "MMD Model: Miku Hatsune ver.2.3\r\n"+
                "(Physical Model)\r\n"+
                "\r\n"+
                "Modeling by	Animasa\r\n"+
                "Converted by	Animasa\r\n"+
                "Copyright		CRYPTON FUTURE MEDIA, INC"),
                model.english_comment)

        self.assertEqual(12354,  len(model.vertices))
        self.assertEqual(22961 * 3,  len(model.indices))
        print("{0} textures".format(len(model.textures)))
        self.assertEqual(17,  len(model.materials))
        self.assertEqual(140,  len(model.bones))
        self.assertEqual(30,  len(model.morphs))
        self.assertEqual(9,  len(model.display_slots))
        self.assertEqual(45,  len(model.rigidbodies))
        self.assertEqual(27,  len(model.joints))

