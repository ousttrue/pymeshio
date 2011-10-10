#!/usr/bin/env python
# coding: utf-8

from setuptools import setup
import sys
import os
import shutil

name='pymeshio'
version='2.2.1'
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

    >>> import pymeshio.pmx.reader
    >>> m=pymeshio.pmx.reader.read_from_file('resources/初音ミクVer2.pmx')
    >>> print(m)
    <pmx-2.0 "Miku Hatsune" 12354vertices>
    >>> print(dir(m))
    ['__class__', '__delattr__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', 'bones', 'comment', 'display_slots', 'english_comment', 'english_name', 'indices', 'joints', 'materials', 'morphs', 'name', 'rigidbodies', 'textures', 'version', 'vertices']

ToDo
--------

* pmd to pmx converter
* update blender25 plugin to blender26
* blender26 importer for pmx
* blender26 exporter for pmx


New
-------
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

