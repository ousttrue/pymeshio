from setuptools import setup
import sys

name='pymeshio'
version='1.9.2'
short_description='pure python 3d model io library'
long_description='''\
`pymeshio` is a package for 3d model io.
create for blender import/expoert plugin backend.

Requirements
------------
* Python 3

Features
--------
* read/write Metasequioa mqo format
* read/write MikuMikuDance pmd format
* read/write MikuMikuDance vmd format
* read/write MikuMikuDance vpd format

Setup
-----
::

   $ easy_install pymeshio
   or
   $ unzip pymeshio-x.x.x.zip
   $ cd pymeshio-x.x.x
   $ python setup.py install

History
-------
1.9.2 (2011-9-29)
~~~~~~~~~~~~~~~~~~
* add tkinter viewer sample

1.9.1 (2011-9-23)
~~~~~~~~~~~~~~~~~~
* register pypi
'''

classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: zlib/libpng License',
        'Topic :: Multimedia :: Graphics :: 3D Modeling',
        ]

setup(
        name=name,
        version=version,
        description=short_description,
        long_description=long_description,
        classifiers=classifiers,
        keywords=['mqo', 'pmd', 'vmd', 'vpd', 'mmd', 'blender'],
        author='ousttrue',
        author_email='ousttrue@gmail.com',
        url='http://meshio.sourceforge.jp/',
        license='zlib',
        package_dir={
            'pymeshio': 'blender25-meshio/pymeshio'
            },
        packages=['pymeshio'],
        test_suite='nose.collector',
        tests_require=['Nose'],
        zip_safe = (sys.version>="2.5"),   # <2.5 needs unzipped for -m to work
        )

