`pymeshio` is a package for 3d model io.
create for blender import/expoert plugin backend.

URL
---
* http://meshio.sourceforge.jp/
* http://pypi.python.org/pypi/pymeshio/

API
~~~
* http://packages.python.org/pymeshio/

Source
~~~~~~
* https://github.com/ousttrue/pymeshio

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

Packaging
---------
::

   $ python setup.py sdist

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
2.4.1 (2012-01-16)
~~~~~~~~~~~~~~~~~~
* bug fix for unsigend integer write(-1 -> 255/66535/4294967295)

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

