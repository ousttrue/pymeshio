# coding: utf-8
import sys
import io
import unittest
import pymeshio.common
import pymeshio.pmd
import pymeshio.pmd.reader
import pymeshio.pmd.writer


PMD_FILE=pymeshio.common.unicode('resources/初音ミクVer2.pmd')


class TestPmd(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_read(self):
        model=pymeshio.pmd.reader.read_from_file(PMD_FILE)
        self.assertEqual(pymeshio.pmd.Model,  model.__class__)
        self.assertEqual(pymeshio.common.unicode('初音ミク').encode('cp932'),  model.name)
        self.assertEqual(pymeshio.common.unicode('Miku Hatsune').encode('cp932'),  model.english_name)
        self.assertEqual(pymeshio.common.unicode(
            "PolyMo用モデルデータ：初音ミク ver.2.3\n"+
            "(物理演算対応モデル)\n"+
            "\n"+
            "モデリング	：あにまさ氏\n"+
            "データ変換	：あにまさ氏\n"+
            "Copyright	：CRYPTON FUTURE MEDIA, INC").encode('cp932'),
            model.comment)
        self.assertEqual(pymeshio.common.unicode(
            "MMD Model: Miku Hatsune ver.2.3\n"+
            "(Physical Model)\n"+
            "\n"+
            "Modeling by	Animasa\n"+
            "Converted by	Animasa\n"+
            "Copyright		CRYPTON FUTURE MEDIA, INC").encode('cp932'),
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
        # read and write to out
        model=pymeshio.pmd.reader.read(io.BytesIO(buf))
        out=io.BytesIO()
        pymeshio.pmd.writer.write(out, model)
        # read out buffer again
        model2=pymeshio.pmd.reader.read(io.BytesIO(out.getvalue()))
        model.diff(model2)
        self.assertEqual(model, model2)

