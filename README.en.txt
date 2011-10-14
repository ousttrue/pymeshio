========
pymeshio
========
http://meshio.sourceforge.jp/

this is blender addon for pmd & mqo.

packaging
===========
$ python setup.py sdist

install blender-2.5x addon
===============================
unzip archive, then exist blender25-meshio directory.
copy the directory to {blender2.5x install directory}/2.5x/scripts/addons.

launch blender, then menu (File)-(User Preferences).
select (Add-Ons) tab.

find "meshio. (.pmd)(.mqo)" and check.

history
========
20111015 2.3.0
--------------
update for blender2.6
implement pmx_importer


20110918 1.9.0
--------------
update for blender2.59
fix mqo export
