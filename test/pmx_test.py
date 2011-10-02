# coding: utf-8
import pymeshio.pmx.loader
import unittest


PMX_FILE=u'resources/初音ミクVer2.pmx'


class TestPmx(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_read(self):
        model=pymeshio.pmx.loader.load(PMX_FILE)
        self.assertEqual(pymeshio.pmx.Model,  model.__class__)
        self.assertEqual(u'初音ミク',  model.name)
        self.assertEqual(u'Miku Hatsune',  model.english_name)
        self.assertEqual(
                u"PolyMo用モデルデータ：初音ミク ver.2.3\r\n"+
                u"(物理演算対応モデル)\r\n"+
                u"\r\n"+
                u"モデリング	：あにまさ氏\r\n"+
                u"データ変換	：あにまさ氏\r\n"+
                u"Copyright	：CRYPTON FUTURE MEDIA, INC",
                model.comment)
        self.assertEqual(
                u"MMD Model: Miku Hatsune ver.2.3\r\n"+
                u"(Physical Model)\r\n"+
                u"\r\n"+
                u"Modeling by	Animasa\r\n"+
                u"Converted by	Animasa\r\n"+
                u"Copyright		CRYPTON FUTURE MEDIA, INC",
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

