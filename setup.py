#!/usr/bin/env python
# coding: utf-8

from setuptools import setup
import sys
import os
import shutil

name='pymeshio'
version='2.2.3'
short_description='3d model io library for mqo, pmd, pmx, vmd and vpd'
long_description='''\
`pymeshio` is a package for 3d model io.
create for blender import/expoert plugin backend.

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

Install
-------
::

   $ easy_install pymeshio
   or
   $ unzip pymeshio-x.x.x.zip
   $ cd pymeshio-x.x.x
   $ python setup.py install

Usage
-----
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


ToDo
--------

* update blender25 plugin to blender26
* blender26 importer for pmx
* blender26 exporter for pmx


New
-------
2.2.3 (2011-10-12)
~~~~~~~~~~~~~~~~~~
* fix for pmxmca

2.2.2 (2011-10-10)
~~~~~~~~~~~~~~~~~~
* add pmd2pmx script

2.2.1 (2011-10-07)
~~~~~~~~~~~~~~~~~~
* implement pmd to pmx converter

2.2.0 (2011-10-03)
~~~~~~~~~~~~~~~~~~
* implement pmx writer

'''

classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: zlib/libpng License',
        'Topic :: Multimedia :: Graphics :: 3D Modeling',
        ]

# copy pymeshio dir for blender25 plugin
PYMESHIO_DIR_IN_BLENDER='blender25-meshio/pymeshio'
if os.path.exists(PYMESHIO_DIR_IN_BLENDER):
    shutil.rmtree(PYMESHIO_DIR_IN_BLENDER)    
print("copy pymeshio to blender-25")
shutil.copytree('pymeshio', PYMESHIO_DIR_IN_BLENDER)

setup(
        name=name,
        version=version,
        description=short_description,
        long_description=long_description,
        classifiers=classifiers,
        keywords=['mqo', 'pmd', 'pmx', 'vmd', 'vpd', 'mmd', 'blender'],
        author='ousttrue',
        author_email='ousttrue@gmail.com',
        url='http://meshio.sourceforge.jp/',
        license='zlib',
        #package_dir={
        #    'pymeshio': 'blender25-meshio/pymeshio'
        #    },
        packages=['pymeshio'],
        test_suite='nose.collector',
        tests_require=['Nose'],
        zip_safe = (sys.version>="2.5"),   # <2.5 needs unzipped for -m to work
        entry_points = {
            'console_scripts': [
                'pmd2pmx = pymeshio.main:pmd_to_pmx',
                ]
            }
        )

