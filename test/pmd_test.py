# coding: utf-8
import sys
import io
import unittest
import pymeshio.pmd
import pymeshio.pmd.loader
import pymeshio.pmd.writer


PMD_FILE=u'resources/初音ミクVer2.pmd'


def test_old_pmd_load():
    loader=pymeshio.pmd.IO()
    assert loader.read(PMD_FILE)


class TestPmd(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_load(self):
        model=pymeshio.pmd.loader.load_from_file(PMD_FILE)
        self.assertEqual(pymeshio.pmd.Model,  model.__class__)
        self.assertEqual(u'初音ミク'.encode('cp932'),  model.name)
        self.assertEqual(u'Miku Hatsune'.encode('cp932'),  model.english_name)
        self.assertEqual((
            u"PolyMo用モデルデータ：初音ミク ver.2.3\n"+
            u"(物理演算対応モデル)\n"+
            u"\n"+
            u"モデリング	：あにまさ氏\n"+
            u"データ変換	：あにまさ氏\n"+
            u"Copyright	：CRYPTON FUTURE MEDIA, INC").encode('cp932'),
            model.comment)
        self.assertEqual((
            u"MMD Model: Miku Hatsune ver.2.3\n"+
            u"(Physical Model)\n"+
            u"\n"+
            u"Modeling by	Animasa\n"+
            u"Converted by	Animasa\n"+
            u"Copyright		CRYPTON FUTURE MEDIA, INC").encode('cp932'),
            model.english_comment)
        self.assertEqual(12354,  len(model.vertices))
        self.assertEqual(22961 * 3,  len(model.indices))
        print("{0} textures".format(len(model.toon_textures)))
        self.assertEqual(17,  len(model.materials))
        self.assertEqual(140,  len(model.bones))
        self.assertEqual(31,  len(model.morphs))
        self.assertEqual(45,  len(model.rigidbodies))
        self.assertEqual(27,  len(model.joints))

    def test_write(self):
        # read source file
        buf=pymeshio.common.readall(PMD_FILE)
        # load and write to out
        model=pymeshio.pmd.loader.load(io.BytesIO(buf))
        out=io.BytesIO()
        pymeshio.pmd.writer.write(out, model)
        # read out buffer again
        model2=pymeshio.pmd.loader.load(io.BytesIO(out.getvalue()))
        self.assertEqual(model, model2)

