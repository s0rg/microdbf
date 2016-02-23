#!/usr/bin/env python
import os
import sys
import microdbf

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()

elif sys.argv[-1] == "build":
    os.system("python setup.py sdist")
    sys.exit()

elif sys.argv[-1] == "test":
    os.system("python3 -m unittest parser_test.py")
    sys.exit()

setup(
    name='microdbf',
    version=microdbf.__version__,
    description='Tiny pure python stream-oriented dbf reader',
    long_description=open('README.md', 'rt').read(),
    author=microdbf.__author__,
    author_email=microdbf.__email__,
    package_data={'': ['LICENSE']},
    package_dir={'microdbf': 'microdbf'},
    packages = ['microdbf'],
    include_package_data=True,
    zip_safe=True,
    install_requires=[],
    license='MIT',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
    ),
)
