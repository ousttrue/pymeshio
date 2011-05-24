#from distutils.core import setup
import sys
from setuptools import setup

setup(
        name='pymeshio',
        version='1.8.4',
        description='pure python 3d model io library',
        keywords=[],
        author='ousttrue',
        author_email='ousttrue@gmail.com',
        url='http://meshio.sourceforge.jp/',
        license='zlib',
        package_dir={
            'pymeshio': 'blender25-meshio/pymeshio'
            },
        packages=['pymeshio'],
        test_suite='nose.collector',
        zip_safe = (sys.version>="2.5"),   # <2.5 needs unzipped for -m to work
        )

