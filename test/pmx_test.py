# coding: utf-8
import pymeshio.pmx.loader


PMX_FILE=u'resources/初音ミクVer2.pmx'

def test_read():
    model=pymeshio.pmx.loader.load(PMX_FILE)
    assert model.__class__==pymeshio.pmx.Model
    assert model.name==u'初音ミク'
    assert model.english_name==u'Miku Hatsune'
    assert model.comment==(
            u"PolyMo用モデルデータ：初音ミク ver.2.3\r\n"+
            u"(物理演算対応モデル)\r\n"+
            u"\r\n"+
            u"モデリング	：あにまさ氏\r\n"+
            u"データ変換	：あにまさ氏\r\n"+
            u"Copyright	：CRYPTON FUTURE MEDIA, INC"
            )
    assert model.english_comment==(
            u"MMD Model: Miku Hatsune ver.2.3\r\n"+
            u"(Physical Model)\r\n"+
            u"\r\n"+
            u"Modeling by	Animasa\r\n"+
            u"Converted by	Animasa\r\n"+
            u"Copyright		CRYPTON FUTURE MEDIA, INC"
            )

    assert len(model.vertices)==12354
    assert len(model.indices)==22961 * 3
    print("{0} textures".format(len(model.textures)))
    assert len(model.materials)==17
    assert len(model.bones)==140
    assert len(model.morphs)==30
    assert len(model.display_slots)==9
    assert len(model.rigidbodies)==45
    assert len(model.joints)==27
