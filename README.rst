`pymeshio` is a package for 3d model io.
create for blender import/expoert plugin backend.

URL
---
* http://pypi.python.org/pypi/pymeshio/
* https://github.com/ousttrue/pymeshio

* http://meshio.sourceforge.jp/

Requirements
------------
* Python 3
* Python 2.7

Features
--------
* read       Metasequioa mqo format
* read/write MikuMikuDance pmd format
* read/write MikuMikuDance pmx format
* read       MikuMikuDance vmd format
* read       MikuMikuDance vpd format
* convert    MikuMikuDance pmd format to MikuMikuDance pmx format
* blender-2.6 import/export plugin


Install as python module
------------------------
from internet
~~~~~~~~~~~~~
::

   $ easy_install pymeshio

from archive
~~~~~~~~~~~~
::

   $ unzip pymeshio-x.x.x.zip
   $ cd pymeshio-x.x.x
   $ python setup.py install

Install as blender-2.6x addon
-------------------------------
Copy
~~~~
unzip archive, then exist blender26-meshio directory.
copy `blender26-meshio` directory to ${blender directory}/2.6x/scripts/addons.

Directory layout
~~~~~~~~~~~~~~~~
::

    ${blender directory}/2.6x/scripts/addons/
      +- blender26-meshio
           +- exporter
           +- pymeshio

Blender user preference
~~~~~~~~~~~~~~~~~~~~~~~
launch blender, then menu (File)-(User Preferences).
select (Add-Ons) tab.

find "meshio. (.pmd)(.mqo)" and check.

Usage as python module
----------------------
::

    >>> import pymeshio.pmd.reader
    >>> m=pymeshio.pmd.reader.read_from_file('resources/初音ミクVer2.pmd')
    >>> print(m)
    <pmd-1, "初音ミク" vertex: 12354, face: 68883, material: 17, bone: 140 ik: 7, skin: 31>
    >>> import pymeshio.converter
    >>> pmx_model=pymeshio.converter.pmd_to_pmx(m)
    >>> print(pmx_model)
    <pmx-2.0 "Miku Hatsune" 12354vertices>
    >>> import pymeshio.pmx.writer
    >>> import io
    >>> pymeshio.pmx.writer.write(io.open("out.pmx", "wb"), pmx_model)
    True
    >>> import pymeshio.vmd.reader
    >>> pymeshio.vmd.reader.read_from_file('resources/motion.vmd')
    <VMDLoader model: "初音ミク", motion: 16897, shape: 997, camera: 0, light: 0>


New
---

2.7.11 (2015-06-03)
~~~~~~~~~~~~~~~~~~
* fix exporter. https://github.com/ousttrue/pymeshio/issues/23, https://github.com/ousttrue/pymeshio/issues/25

2.7.10 (2015-05-04)
~~~~~~~~~~~~~~~~~~
* fix exporter. https://github.com/ousttrue/pymeshio/issues/20
* fix material alpha(pmd export, pmx export)  

2.7.9 (2014-12-20)
~~~~~~~~~~~~~~~~~~
* fix mqo export(from blender 2.63?). thanks to sapper-trle

2.7.8 (2013-10-16)
~~~~~~~~~~~~~~~~~~
* import obj reader(face)
 
2.7.7 (2013-09-20)
~~~~~~~~~~~~~~~~~~
* implement obj reader
* implement morph for vmd.writer

2.7.6 (2013-09-18)
~~~~~~~~~~~~~~~~~~
* fix empty tessfaces when modifier_apply(from blender 2.66?)

2.7.5 (2013-07-06)
~~~~~~~~~~~~~~~~~~
* implement read pmx BoneMorph
* implement read pmx GroupMorph

2.7.4 (2013-04-29)
~~~~~~~~~~~~~~~~~~
* fix pmx_importer. https://github.com/ousttrue/pymeshio/issues/15 

2.7.3 (2013-03-02)
~~~~~~~~~~~~~~~~~~
* add vmd writer
* add x reader
* add x writer

2.7.2 (2013-01-13)
~~~~~~~~~~~~~~~~~~
* fix for blender-2.65

2.7.1 (2012-10-21)
~~~~~~~~~~~~~~~~~~
* fix pmd/pmx export mesh without material  

2.7.0 (2012-09-05)
~~~~~~~~~~~~~~~~~~
* merge griffon-9's pmx bdef4 export implementation
* merge griffon-9's pmx unsigned short bug fix
* merge griffon-9's morph assertion buf fix
* merge griffon-9's shapre group implovement
* fix mqo import
* remove 16 material limitation from mqo/pmd/pmx import(not split mesh)

2.6.5 (2012-06-13)
~~~~~~~~~~~~~~~~~~
* fix and implovement vertex morph for pmd/pmx exporter. thanks to griffon-9

2.6.4 (2012-05-30)
~~~~~~~~~~~~~~~~~~
* implement toon texture for pmd. thanks to griffon-9
* fix ik_target index for pmd. thanks to griffon-9

2.6.3 (2012-05-18)
~~~~~~~~~~~~~~~~~~
* fix pmx writing for utf-16-le. change default encoding to utf-16-le

2.6.2 (2012-05-17)
~~~~~~~~~~~~~~~~~~
* fix export_pmd bug that flip face. thanks to griffon-9

2.6.1 (2012-05-03)
~~~~~~~~~~~~~~~~~~
* implement pmd importer/exporter

2.6.0 (2012-04-30)
~~~~~~~~~~~~~~~~~~
* fix pmd importer/exporter for blender2.63
* it cannot be used in blender2.62

2.5.6 (2012-04-22)
~~~~~~~~~~~~~~~~~~
* restore blender pmd importer/exporter
* fix englishmap

2.5.5 (2012-04-17)
~~~~~~~~~~~~~~~~~~
* blender pmx importer/exporter improvement
    * fix lost bones
    * fix bone order
    * implement bone flags
    * fix lost uv
    * copy rotation
    * fix fixed_axis in convert 

2.5.4 (2012-04-15)
~~~~~~~~~~~~~~~~~~
* fix face flip for pmx_importer/pmx_export
* implement material flags for pmx_importer/pmx_export

2.5.3 (2012-04-14)
~~~~~~~~~~~~~~~~~~
* update pmd to pmx converter(bone flag)
* use face normal when the face is not smooth
* implement ik-limit for pmx_importer

2.5.2 (2012-04-11)
~~~~~~~~~~~~~~~~~~
* update pmd to pmx converter(bone group)

2.5.1 (2012-03-06)
~~~~~~~~~~~~~~~~~~
* fix pmd importer/exporter rigid w h d

2.5.0 (2012-03-03)
~~~~~~~~~~~~~~~~~~
* implement camera motion for vmd

2.4.3 (2012-01-19)
~~~~~~~~~~~~~~~~~~
* treat a no child bone that tail_index is 0xFFFF
  (for 2.4.1 export model. tail_index specification ?)

2.4.2 (2012-01-17)
~~~~~~~~~~~~~~~~~~
* fix critical bug, no morph data(pmd_export).

2.4.1 (2012-01-16)
~~~~~~~~~~~~~~~~~~
* fix bug, unsigend integer write(-1 -> 255/66535/4294967295)

2.4.0 (2012-01-13)
~~~~~~~~~~~~~~~~~~
* implement BDEF4 and SDEF for pmx
* implement MaterialMorph for pmx

2.3.3 (2011-12-02)
~~~~~~~~~~~~~~~~~~
* fix pymeshio.vmd

2.3.2 (2011-11-07)
~~~~~~~~~~~~~~~~~~
* fix for blender-2.6

2.3.1 (2011-10-15)
~~~~~~~~~~~~~~~~~~
* bug fix(pmd_to_pmx RigidBody.shape_position)
* implement pmx_importer

2.2.4 (2011-10-13)
~~~~~~~~~~~~~~~~~~
* bug fix(__init__ param)
* fix blender-2.5 plugin for blender-2.6

Upload to pypy
---------
::

   $ python setup.py sdist --formats=zip upload

