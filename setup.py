#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages
import sys
import os
import shutil
import codecs


# copy pymeshio dir for blender26 plugin
PYMESHIO_DIR_IN_BLENDER26='blender26-meshio/pymeshio'
if os.path.exists(PYMESHIO_DIR_IN_BLENDER26):
    shutil.rmtree(PYMESHIO_DIR_IN_BLENDER26)    
print("copy pymeshio to %s" % PYMESHIO_DIR_IN_BLENDER26)
shutil.copytree('pymeshio', PYMESHIO_DIR_IN_BLENDER26)


setup(
        name='pymeshio',
        version='2.8.2',
        description='3d model io library for mqo, pmd, pmx, vmd and vpd',
        long_description=codecs.open('README.rst', 'r', 'utf-8').read(),
        classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: zlib/libpng License',
            'Topic :: Multimedia :: Graphics :: 3D Modeling',
            ],
        keywords=['mqo', 'pmd', 'pmx', 'vmd', 'vpd', 'mmd', 'blender'],
        author='ousttrue',
        author_email='ousttrue@gmail.com',
        url='https://pypi.python.org/pypi/pymeshio/',
        license='zlib',
        packages=find_packages(),
        test_suite='nose.collector',
        tests_require=['Nose'],
        zip_safe = (sys.version>="2.5"),   # <2.5 needs unzipped for -m to work
        entry_points = {
            'console_scripts': [
                'pmd2pmx = pymeshio.main:pmd_to_pmx',
                'pmd_diff = pymeshio.main:pmd_diff',
                'pmd_validator = pymeshio.main:pmd_validator',
                ]
            }
        )

