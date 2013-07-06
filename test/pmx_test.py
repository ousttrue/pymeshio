# coding: utf-8
import unittest
import io
import pymeshio.common
import pymeshio.pmd.reader
import pymeshio.pmx.reader
import pymeshio.pmx.writer


PMX_FILE=pymeshio.common.unicode('resources/初音ミクVer2.pmx')
PMX_FILE_WITH_BONEMORPH=pymeshio.common.unicode('resources/bonemorph.pmx')


class TestPmx(unittest.TestCase):
    
    def setUp(self):
        pass

    def test_read(self):
        model=pymeshio.pmx.reader.read_from_file(PMX_FILE)
        self.assertEqual(pymeshio.pmx.Model,  model.__class__)
        self.assertEqual(pymeshio.common.unicode('初音ミク'),  model.name)
        self.assertEqual(pymeshio.common.unicode('Miku Hatsune'),  model.english_name)
        self.assertEqual(pymeshio.common.unicode(
                "PolyMo用モデルデータ：初音ミク ver.2.3\r\n"+
                "(物理演算対応モデル)\r\n"+
                "\r\n"+
                "モデリング	：あにまさ氏\r\n"+
                "データ変換	：あにまさ氏\r\n"+
                "Copyright	：CRYPTON FUTURE MEDIA, INC"),
                model.comment)
        self.assertEqual(pymeshio.common.unicode(
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

    def test_write(self):
        # read source file
        buf=pymeshio.common.readall(PMX_FILE)
        # read and write to out
        model=pymeshio.pmx.reader.read(io.BytesIO(buf))
        out=io.BytesIO()
        pymeshio.pmx.writer.write(out, model)
        # read out buffer again
        model2=pymeshio.pmx.reader.read(io.BytesIO(out.getvalue()))
        self.assertEqual(model, model2)

    def test_bonemorph(self):
        model=pymeshio.pmx.reader.read_from_file(
                PMX_FILE_WITH_BONEMORPH)

