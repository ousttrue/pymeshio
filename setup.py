#from distutils.core import setup
import sys
from setuptools import setup

setup(
        name='pymeshio',
        version='1.9.0',
        description='pure python 3d model io library',
        classfiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: zlib/libpng License',
            'Topic :: Multimedia :: Graphics :: 3D Modeling',
            ],
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

