#!/bin/env -e python
from distutils.core import setup
import fido.run

setup(name='fido',
      version=fido.run.version,
      scripts=['fido/fido.bat','fido/fido.sh'],
      #options={"py2exe": { }},
      url="http://github.com/openplanets/fido",
      #packages=['fido'],
      py_modules=['fido.run', 'fido.formats', 'fido.signature', 'fido.testfido', 'fido.argparselocal'],
      description='Format Identification for Digital Objects (FIDO).',
      author='Adam Farquhar',
      author_email='adam.farquhar@bl.uk',
      license='Apache 2.0 - See License.txt',
    classifiers=[
    "Programming Language :: Python :: 2.7",
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Apache Software License"
    ]
      )
