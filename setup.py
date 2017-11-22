#!/usr/bin/env python
# coding: utf-8
from logging import getLogger
logger = getLogger(__name__)
from logging import basicConfig, DEBUG
basicConfig(level=DEBUG)

import sys
import re
import codecs
import os
import shutil
from zipfile import ZipFile
from setuptools import setup, find_packages, Command

try:
    import nose
except ImportError:
    logger.warning('no nose')


class BlenderAddOn(Command):

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # cleanup
        dst = 'pymeshio_addon'
        if os.path.exists(dst):
            logger.debug('clear %s', dst)
            shutil.rmtree(dst)

        logger.debug('copy blender addon')
        shutil.copytree('blender26-meshio', dst,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copytree('pymeshio', dst + '/pymeshio',
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

        # archive
        with ZipFile(dst + '.zip', 'w') as myzip:
            for root, dirs, files in os.walk(dst):
                for file in files:
                    path = os.path.join(root, file)
                    logger.debug('archive: %s', path)
                    myzip.write(path)


version = ''
with open('pymeshio/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)
if not version:
    raise RuntimeError('Cannot find version information')


setup(
    name='pymeshio',
    version=version,
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
    zip_safe=(sys.version >= "3.4"),   # <2.5 needs unzipped for -m to work
    entry_points={
        'console_scripts': [
            'pmd2pmx = pymeshio.main:pmd_to_pmx',
            'pmd_diff = pymeshio.main:pmd_diff',
            'pmd_validator = pymeshio.main:pmd_validator',
        ]},
    cmdclass={'blender': BlenderAddOn})
