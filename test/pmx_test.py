# coding: utf-8
import pymeshio.pmx.loader


PMX_MODEL='resources/初音ミクVer2.pmx'

def test_read():
    model=pymeshio.pmx.loader.load(PMX_MODEL)
    assert model.__class__==pymeshio.pmx.Model
    assert model.name=='初音ミク'
    assert model.english_name=='Miku Hatsune'
    assert model.comment==(
            "PolyMo用モデルデータ：初音ミク ver.2.3\r\n"+
            "(物理演算対応モデル)\r\n"+
            "\r\n"+
            "モデリング	：あにまさ氏\r\n"+
            "データ変換	：あにまさ氏\r\n"+
            "Copyright	：CRYPTON FUTURE MEDIA, INC"
            )
    assert model.english_comment==(
            "MMD Model: Miku Hatsune ver.2.3\r\n"+
            "(Physical Model)\r\n"+
            "\r\n"+
            "Modeling by	Animasa\r\n"+
            "Converted by	Animasa\r\n"+
            "Copyright		CRYPTON FUTURE MEDIA, INC"
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
